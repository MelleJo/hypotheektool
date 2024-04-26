import streamlit as st
import os
from docx import Document
from PyPDF2 import PdfReader
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.chains import AnalyzeDocumentChain
from langchain.chains.question_answering import load_qa_chain
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

# Definieer globale variabelen voor de paden
motivatieteksten_path = "source documents/Teksten voor hypotheekadviesrapport in Fastlane (in concept, MvdB).docx"
sjabloon_path = "source documents/Hyp. rapport zonder motivatieteksten.pdf"

def generate_report(user_input):
    with st.spinner('Verwerken...'):
        # Ensure the output directory exists
        output_dir = 'output'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Load motivational texts and template
        motivatieteksten_doc = Document(motivatieteksten_path)
        sjabloon_reader = PdfReader(sjabloon_path)

        # Build the AI prompt
        template = """
        Analyseer de opgegeven input, haal op basis hiervan relevante motivatieteksten uit het document en verwerk deze in het sjabloon.
        Zorg ervoor dat het rapport, afgezien van de namen, volledig voorbereid is en vul zoveel mogelijk in. Exporteer dit vervolgens als een .docx-bestand.
        """
        prompt = ChatPromptTemplate.from_template(template)

        # Set up the LangChain LLM chain
        llm = ChatOpenAI(api_key=st.secrets["OPENAI_API_KEY"], model="gpt-4-turbo-2024-04-09", temperature=0, streaming=True)
        chain = prompt | llm | StrOutputParser()

        # Execute chain
        document_text = ' '.join([para.text for para in motivatieteksten_doc.paragraphs])
        output = chain.stream({
            "document_text": document_text,
            "user_input": user_input,
        })

        # Save output to a .docx file
        output_doc = Document()
        output_doc.add_paragraph(output)
        output_path = os.path.join(output_dir, 'Hypotheek_Rapport.docx')
        output_doc.save(output_path)
        return output_path

def main():
    st.title("Hypotheektool - Testversie 0.0.1")
    user_input = st.text_input("Geef informatie over het hypotheek adviestraject. Voeg hier geen persoonlijk identificeerbare informatie toe; deze details kun je later toevoegen.")
    if st.button("Rapport Genereren"):
        report_path = generate_report(user_input)
        if os.path.exists(report_path):
            with open(report_path, "rb") as file:
                st.success('Rapport succesvol gegenereerd.')
                st.download_button(
                    label="Download Rapport",
                    data=file,
                    file_name="Hypotheek_Rapport.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
        else:
            st.error("Er is een fout opgetreden bij het genereren van het rapport.")

if __name__ == "__main__":
    main()
