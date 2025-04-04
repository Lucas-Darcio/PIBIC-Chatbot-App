import os
import sys
import streamlit as st

# Adiciona o diretório raiz ao PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.business_logic.resume_processor import process_resume
from app.business_logic.query_handler import  extract_attributes_chatbot, handle_query_chat

from app.data_access.file_manager import list_curriculos, load_curriculo
#from app.services.email_service import send_email

from app.business_logic.compression_utils import extract_prompt_tags

from app.api.openai_api import extract_related_tags

# Diretório onde os currículos armazenados ficam
CURRICULO_DIR = "curriculos/"

# Caminho para o arquivo JSON
CONSULTAS_DIR = "consultas/"


def main():
    st.set_page_config(
        page_title="Converse com o currículo",
        layout="wide"
    )

    st.title("Converse com o currículo")

    if 'disable_chat_bool' not in st.session_state:
        st.session_state.disable_chat_bool = True  # 'value'

    # disable_chat_bool = True
    curriculo_name = ""

    with st.sidebar:

        passos = '''1 - Envie ou selecione um currículo no formato XML.   
        2 - Confirme a seleção de currículo para que ele vá para o contexto.   
        3 - Utilize o chat para realizar as atividades.   
'''

        # cont_height = 500
        st.header("Escolher Currículo")
        st.markdown(passos)

        # Upload de novo currículo
        uploaded_file = st.sidebar.file_uploader(
            "Faça upload de um currículo (XML)", type="xml")

        # Exibe currículos existentes no diretório
        stored_resumes = list_curriculos(CURRICULO_DIR)
        selected_resume = st.sidebar.selectbox(
            "Ou escolha um currículo existente do nosso banco de dados", stored_resumes)

        if uploaded_file:
            # curriculo_data = load_curriculo(os.path.join(CURRICULO_DIR, selected_resume))
            curriculo_data = process_resume(load_curriculo(uploaded_file))
            curriculo_name = uploaded_file.name
            st.sidebar.write(f"Currículo escolhido: {curriculo_name}")
        else:
            curriculo_data = process_resume(
                os.path.join(CURRICULO_DIR, selected_resume))
            curriculo_name = selected_resume
            st.sidebar.write(f"Currículo escolhido: {curriculo_name}")

        if st.button("Confirmar currículo", type="primary"):
            # Escolha final do currículo: preferindo o upload se houver
            print(st.session_state.disable_chat_bool)
            st.session_state.disable_chat_bool = not st.session_state.disable_chat_bool
            print(st.session_state.disable_chat_bool)

    if not st.session_state.disable_chat_bool:

        st.warning(f"curriculo {curriculo_name} carregado!")

    # Inicia o o historico de mensagens na sessão
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # exibe o historico das mensganes
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # esntrando
    user_input = st.chat_input(
        placeholder="Digite sua tarefa ou pergunta...", disabled=st.session_state.disable_chat_bool)
    
    if user_input:
        #adiciona a mensagem do usuario ao historico
        st.session_state.messages.append({"role": "user", "content": user_input})
        

        with st.spinner("Carregando..."):
            #bot_reply = f"Chatbot: {user_input}"
            #bot_reply = openaiChat(user_input)


            # CHAT analise o prompt e retorna tags relacionadas ao prompt, é uma string
            tags_relacionadas = extract_related_tags(user_input)
            print(tags_relacionadas)
            
            # extrair tags (assuntos) alinhados com o prompt, lista de strings
            tags_alinhadas = extract_prompt_tags(tags_relacionadas)
            print("TAGS ALINHADAS:\n")
            print(tags_alinhadas)

            # manda o prompt do usuário separado das tags alinhadas
            processed_data = extract_attributes_chatbot(tags_alinhadas, curriculo_data)
            # print(processed_data)
            

            if processed_data:
                bot_reply = handle_query_chat(processed_data, user_input)[0]
                #bot_reply = "rodando..."
                print("Bot reply")
                print(bot_reply)
        
            else:
                with st.chat_message("assistant"):
                    st.markdown("erro em curriculo_data")
                
        #Adiciona a resposta do chatbot ao historico
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})

        #atualiza a interface com a nova resposta
        with st.chat_message("user"):
            st.markdown(user_input)
            
        with st.chat_message("assistant"):
            st.markdown(bot_reply)
        
        

if __name__ == "__main__":
    main()
