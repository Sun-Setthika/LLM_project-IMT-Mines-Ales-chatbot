# **IMT Mines Alès Student Assistant Chatbot **
(AI-Powered Chatbot for International Students)

## Demo
https://github.com/user-attachments/assets/edb68ace-5cac-4bb3-909d-487f17dfb030





File Description:
### ChatBot_Colab is the notebook for fine-tuning with the json dataset
### ChatbotRAG_Colab is the notebook for RAG approach with the same dataset(json)
### ChatbotRagPDF is the notebook for testing RAG with FAQ.pdf of MDE only(not included the json dataset)

## **Project Overview**
This project develops an **AI-powered chatbot** tailored to support **international students** at **IMT Mines Alès** by providing quick and accurate access to essential academic and administrative information. The solution integrates **fine-tuned Meta-Llama-3.1-8B**, enhanced through **LoRA (Low-Rank Adaptation)** and **4-bit quantization**, for a resource-efficient deployment.

Additionally, the project includes a **comparative study** of two development strategies: **Fine-tuning vs. Retrieval-Augmented Generation (RAG)**, to evaluate performance, flexibility, and deployment feasibility.

---

## **Key Features**

| Feature                    | Description                                                                 |
|----------------------------|-----------------------------------------------------------------------------|
| ✅ Academic Assistance     | Answers questions on courses in the **Informatics Department**.             |
| ✅ Housing Guidance        | Provides information on **student housing and rental options**.             |
| ✅ Work-Study Support      | Shares details on **internships and work-study contracts**.                 |
| ✅ Multilingual Support    | Handles queries in both **English and French**.                             |
| ✅ Efficient Performance   | Utilizes **LoRA** and **4-bit quantization** for **fast and lightweight** execution. |
| ✅ Dual Approach           | Implements both **fine-tuning** and **RAG-based** solutions.                |

---

## **Technical Approaches**

| Approach              | Description                                                                                  |
|-----------------------|----------------------------------------------------------------------------------------------|
| 🔧 Fine-Tuning        | Fine-tuned **Llama 3.1 8B** with **UnSloth** and **LoRA**, trained on a custom academic dataset. |
| 🔍 RAG (Retrieval-Augmented Generation) | Integrated **Llama 3.1 8B** with **BM25** and **semantic encoder** (`paraphrase-multilingual-MiniLM-L12-v2` or `BAAI/bge-m3`) for hybrid retrieval. |

---

## **Dataset Overview**

The dataset is curated to reflect real-world concerns and queries of international students:

| Category               | Contents                                                                                  |
|------------------------|-------------------------------------------------------------------------------------------|
| 📚 Academic Content    | Detailed information on courses, curricula, and academic requirements in **Informatics & AI**. |
| 🏠 Housing             | Student accommodation options, rental guidance, and application processes.                 |
| 💼 Work-Study Options  | Internship guidelines, contract types, and job search resources for international students. |

---

## **Conclusion**
This project delivers a robust, scalable, and multilingual AI chatbot solution, optimized for the needs of international students at IMT Mines Alès. By evaluating both **fine-tuned** and **RAG-based** methods, it offers insights into performance trade-offs and practical implementation choices for academic AI assistants.
