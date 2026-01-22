######################################## 
############ FUNCIONALIDADES ############ 
######################################## 

############ VISÃO CLIENTE ############ 

Dashboard:
- Quando clicar em Contratos Ativos, ir para página de contratos;
- Quando clicar em Consultores Alocados, ir para a página de consultores;
- Quando clicar em Resumo Financeiro, ir para a página de Faturamento;

Contratos:
- Não deve aparecer a função de “+ Novo Contrato” para o cliente;
- Quando o cliente clicar sob o nome de um dos contratos, seja expandida uma tela abaixo, com a lista do histórico de faturamentos, e que neste, possua o anexo do Timesheet que foi validado com o cliente e algumas infos:
    - Timesheet (excel anexo);
    - Número de horas consumidas;
    - Aprovador: nome do aprovador;
    - Data da aprovação;

Consultores:
- Não deve aparecer a função de “+ Novo Consultor” para o cliente;
- Cliente ao clicar sob o nome do consultor, ele possa criar um feedback, e que possa ver o histórico de feedbacks que ele criou, e que o percentual, seja uma média destas notas;
- Tenha o lugar para colocar a foto do consultor, pequena, mas que tenha;

Faturamento:
- Quando o cliente clicar sob o título de um dos contratos, expandir abaixo, a lista de faturas emitidas, pendente pagamento;
    - Além desta visão, para cada linha de faturamento, ao clicar, também deve expandir para as seguintes infos:
        - Número da nota fiscal;
        - Data de faturamento;
        - Prazo de pagamento;
        - Data prevista do pagamento;
        - Data do pagamento.
- O quadro de filtros, pode subir para cima dos quadros de resumo, e que todos os quadros abaixo, respeitem os filtros realizados;
- Quando o cliente clicar em Exportar, seja gerado um excel (csv) ou PDF;
- O campo “+ Nova Parcela” não deve aparecer para cliente;


Clientes:
- Não deve aparecer para os clientes;


############ VISÃO INTERNA ############ 
Funcionalidades Gerais:
- Permissão de edição (inclusão, alteração e delete) para todas as páginas;
- Deve-se ter todas as funcionalidades de usuários clientes, adicionando as funcionalidades de gestão (somando);

Dashboard:
- Contratos ativos - mantém;
- Consultores alocados - mantém;
- Feedback Médio - mantém;
- Total Faturado - mantém;
- Resumo financeiro se mantém, porém, com poucas alterações:
    - Valor total - mantém;
    - Faturado e pago;
    - Pendente pagamento;
    - A faturar;

Contratos:
- Quando clicar sob o nome de um dos contratos, seja expandida uma tela abaixo, com a lista do histórico de faturamentos, e que neste, possua o anexo do Timesheet que foi validado com o cliente e algumas infos:
    - Timesheet (excel anexo);
    - Número de horas consumidas;
    - Aprovador: nome do aprovador;
    - Data da aprovação;
- Quando clicar em “Novo Contrato” aparecer:
    - Nome do Contrato - mantém;
    - Cliente - mantém;
    - Nome do responsável - Adicionar (deve ser selecionável a pessoa cadastrada ao cliente também cadastrado);
    - Valor total - mantém
    - Forma de pagamento - adicionar (a vista / parcelado)
    - Status - mantém;
    - Data de vencimento - mantém;

Consultores:

- Ao clicar sob o nome do consultor, ele possa criar um feedback, e que possa ver o histórico de feedbacks que ele criou, e que o percentual, seja uma média destas notas;
- Tenha o lugar para colocar a foto do consultor, pequena, mas que tenha;
- Ao clicar em “Novo Consultor” deve aparecer:
    - Nome do consultor - mantém;
    - Cargo - mantém;
    - Trocar parceiro por cliente;
    - Contrato - deve ser filtrado pelos contratos do cliente selecionado;
    - Feedback de Performance - Não deve aparecer na tela de cadastro de consultores;

Faturamento:
- Ao clicar sob o título de um dos contratos, expandir abaixo, a lista de faturas emitidas, pendente pagamento;
    - Além desta visão, para cada linha de faturamento, ao clicar, também deve expandir para as seguintes infos:
        - Número da nota fiscal;
        - Data de faturamento;
        - Prazo de pagamento;
        - Data prevista do pagamento;
        - Data do pagamento.
- O quadro de filtros, pode subir para cima dos quadros de resumo, e que todos os quadros abaixo, respeitem os filtros realizados;
- Quando clicar em Exportar, seja gerado um excel (csv) ou PDF;
- Quero um quadro adicional que contabilize os valores inadimplentes, ou seja, valores totais com faturas geradas, e não pago, com data de pagamento limite vencida, e ao clicar, abra uma tela abaixo, demonstrando clientes e contratos inadimplentes;
- Ao clicar em “+ Nova Parcela” deve aparecer:
    - Contrato - mantém;
    - Mês de referência - mantém;
    - Valor - mantém;
    - Número da nota fiscal;
    - Data de faturamento;
    - Prazo de pagamento;
    - Data prevista do pagamento;
    - Data do pagamento.
    - Retirar a flag de marcar como faturado / pago (isso deverá ser feito através do botão que já existe (Marcar pago);

Clientes:
- Resumo - mantém;
- Lista de clientes - mantém;
- Ao clicar em “+ Novo cliente” deve aparecer:
    - Nome do cliente - mantém;
    - CNPJ;
    - Razão social;
    - Parceiro - deve ser retirado por enquanto;

Parceiros:
- Resumo - mantém;
- Lista de parceiros - mantém;
- Ao clicar em “+ Novo Parceiro” deve aparecer:
    - Nome do parceiro;
    - Estratégico ou não;
    - Status;

    