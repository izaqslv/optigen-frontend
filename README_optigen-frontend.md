OptiGen Frontend

Interface interativa para análise inteligente de sedimentação em fluidos.

 Visão Geral

O OptiGen Frontend é uma aplicação desenvolvida em Streamlit que permite ao usuário interagir com os modelos do OptiGen de forma intuitiva, visual e orientada à tomada de decisão.

---

 Funcionalidades

- Sistema de login com autenticação
- Visualização de gráficos experimentais e preditos
- Análise por fluido e altura
- Comparação entre fluidos
- Modo de análise avançada (integração com IA)
- Geração de relatórios técnicos em PDF
- Histórico de simulações

---

 Modos Disponíveis

 Individual

Análise de um fluido em uma altura específica

 Comparação

Comparação entre diferentes fluidos

 Análise Avançada

Execução completa do modelo com geração automática de múltiplos gráficos

---

 Integração

O frontend se comunica com o backend via API REST:

http://127.0.0.1:8010

ou ambiente de produção:

https://optigen.onrender.com

---

 Tecnologias

- Streamlit
- Requests
- ReportLab (PDF)
- PIL (imagens)
- Base64 (transporte de imagens)

---

 Execução Local

streamlit run app.py

---

 Deploy

- Hospedado no Streamlit Cloud
- Integrado com backend no Render

---

 Status do Projeto

 Interface funcional
 Integração backend concluída
 Geração de relatórios ativa

---

 Roadmap

- [ ] Dashboard com métricas avançadas
- [ ] Upload de dados personalizados
- [ ] Interface multiusuário
- [ ] Melhorias de UX/UI

---

 Sobre

Desenvolvido pela NewGen Intelligent Engineering Solutions
Incubada na UNICAMP (INCAMP)

---