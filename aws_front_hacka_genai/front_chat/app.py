import back_genai.answers_facade
from shiny import App, ui
from back_genai import answers_facade
# import answers_facade as answers
app_ui = ui.page_fillable(
    ui.panel_title("arccee"),
    ui.chat_ui("chat",placeholder="Digite a sua mensagem.."),
    fillable_mobile=True,
)
welcome = ui.markdown(
    """
    Olá! Sou o arcce, um assistente de regras da ccee, uma inteligência artificial para sanar dúvidas sobre comercialização de energia.
    """
)


def server(input, output, session):
    chat = ui.Chat(id="chat", messages=[welcome])

    @chat.on_user_submit
    async def _():
        user = chat.user_input()
        res = answers_facade.AnswersFacade({user})
        await chat.append_message(f"llm: "+
                                  res.get_answer_llm())
        await chat.append_message(f"knowledge_base: "+
                                  res.get_answers_base_conhecimento())
        await chat.append_message(f"prompt_flow: "+
                                  res.get_answer_by_flow())


app = App(app_ui, server)
