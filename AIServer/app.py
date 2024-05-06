from openai import OpenAI
from langchain_community.llms import LlamaCpp
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
from langchain_core.prompts import PromptTemplate
from embeddings import load_embeddings

# /TheBloke/Mistral-7B-Instruct-v0.1-GGUF/blob/main/mistral-7b-instruct-v0.1.Q4_K_M.gguf


# conversational RAG
def rag_chain(store_name):
    vector_store = load_embeddings(store_name=store_name, path="./embeddings")

    callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

    llm = LlamaCpp(
        model_path="./models/mistral-7b-instruct-v0.1.Q4_K_M.gguf",
        temperature=0.1,
        max_tokens=200,
        n_gpu_layers=-1,
        top_p=1,
        callback_manager=callback_manager,
        verbose=True,
    )
    print("LLM loaded")

    retriever = vector_store.as_retriever(
        search_type="similarity", search_kwargs={"k": 2}
    )
    print("Retriever loaded")

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=False)

    crc = ConversationalRetrievalChain.from_llm(
        llm=llm, retriever=retriever, memory=memory, chain_type="stuff"
    )
    print("CRC loaded")

    return crc


if __name__ == "__main__":
    crc = rag_chain("instructEmbeddings")
    prompt = "Hi, how are you?"
    print(f"Invoking CRC with prompt: {prompt}")
    result = crc.invoke({"question": prompt})
