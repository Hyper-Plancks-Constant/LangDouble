# **LangDouble**

**LangDouble** é uma aplicação em **Python** com **interface gráfica (Tkinter)** desenvolvida para realizar cálculos utilizando dados experimentais de **Sondas Duplas de Langmuir**.  
O programa automatiza a análise de curvas IxV, o cálculo da temperatura eletrônica \(T_e\) e a determinação da densidade eletrônica \(n_e\), fornecendo gráficos, ajustes e resultados numéricos de forma amigável.

---

## **📌 Funcionalidades principais**

A interface é organizada em **três abas**, cada uma dedicada a uma etapa do diagnóstico por sonda dupla.

---

## **🟦 Aba 1 – Curva IxV da Sonda Dupla**

Para se obter \(T_e\), a primeira etapa é ter um gráfico IxV. Entretanto, como a corrente costuma estar na ordem de µA, é comum utilizar um resistor no circuito para se obter indiretamente o valor da corrente na sonda. Nesta aba, supõe-se que o usuário obteve a tensão (V) em cima da sonda, e a tensão (V) em cima do resistor. Caso o usuário já tiver em mãos o gráfico IxV, pode ignorar esta aba.

**OBSERVAÇÃO:** Para nossos experimentos, utilizamos uma resistência de 502KΩ. Esse valor de resistência pode ser alterado dentro do código fonte, no início da Aba 1.

Nessa aba, é possível construir a curva **IxV** em um gráfico interativo. Essa curva é fundamental, pois dela serão extraídas as informações físicas utilizadas nas abas seguintes.

---

## **🟩 Aba 2 – Cálculo de \(T_e\) (Temperatura Eletrônica)**

Baseado na teoria de sondas duplas, o ponto de inflexão na região positiva da curva IxV permite extrair a **corrente de saturação** que está associada ao valor de \(T_e\).

Nesta aba o usuário pode:

- Ajustar **manualmente** os intervalos de duas retas ajustadas, uma na região positiva apos V=0 e outra na região de saturação, cuja interseção retorna o valor da corrente de saturação;
- Visualizar o ajuste direto no gráfico IxV;
- Calcular automaticamente o valor da **Temperatura eletrônica \(T_e\)**;
- Salvar os dados num arquivo .dat;
- Reiniciar ou refazer o ajuste quantas vezes quiser.
  
---

## **🟧 Aba 3 – Cálculo da Densidade Eletrônica \(n_e\)**

Esta aba permite calcular a densidade eletrônica \(n_e\) a partir da corrente de saturação, da área da sonda e da velocidade de deriva \(v_d\).

A aba:

- Aceita valores em **notação científica** (ex.: `1e5`, `5e-6`);
- Executa o cálculo completo de \(n_e\);
- Permite salvar o valor num arquivo .dat já existente, sem reescrever o arquivo, mas somente acrescentando o dado.

---

## **🖥️ Interface Gráfica**

- Desenvolvida inteiramente em **Tkinter**, fácil de usar.
- Botões, campos e pop-ups claros para cada etapa.
- Gráficos gerados com **matplotlib**, integrados à janela principal.
- Feedback visual imediato durante ajustes e cálculos.

---

## **⚙️ Dependências**

- Python 3.10+
- matplotlib  
- numpy  
- tkinter
- scipy
- pandas

---

## **✉️ Contato**

Caso deseje contribuir, reportar bugs ou sugerir melhorias, fique à vontade!
