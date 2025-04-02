# 基于向量数据库RAG的AI助手

## 项目简介

本项目是一个基于向量数据库RAG（Retrieval-Augmented Generation）本地部署的AI助手，旨在打造一个简单快速安全的本地知识库，为用户提供智能、高效的对话体验。本项目结合向量数据库和Ollama，将用户给定的文档通过嵌入模型存储到chromadb向量数据库中，通过langchain库将用户输入的对话问题转化为向量，通过向量数据库检索到最相关的文档，再通过生成模型生成回答，从而实现智能对话。

**软件&模型**

Ollama、bge-m3、qwen2.5

**技术栈**

langchain、chromadb、flask、flasgger

**Ollama模型迁移**[ollama迁移已下载的单个模型到服务器-CSDN博客](https://blog.csdn.net/A15216110998/article/details/146506117)
