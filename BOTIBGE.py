import logging
import json
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor


logging.basicConfig(level=logging.DEBUG)

API_TOKEN = '1721365780:AAENomaexo7U86BNtJT11BS28bzj0YFpU-w'


bot = Bot(token=API_TOKEN) # , proxy='http://proxy.server:3128'

# For example use simple MemoryStorage for Dispatcher.
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
with open('full.json', 'r') as f:
    full = json.load(f)

# States
class Form(StatesGroup):
    apresentação = State()  # Will be represented in storage as 'Form:name'
    nome = State()  # Will be represented in storage as 'Form:age'
    info = State()  # Will be represented in storage as 'Form:gender'

@dp.message_handler(commands=['info'])
async def send_welcome(message: types.Message):
    await types.ChatActions.typing(0.5)
    await message.reply("Hi! I'm Bot IBGE!\nPowered by:\nDev. Renan Almeida. (Estagiário Developer)\n")


@dp.message_handler(commands='start')
async def cmd_start(message: types.Message):
    await types.ChatActions.typing(0.3)
    with open('user.txt') as file:
        userList = file.read()
    user = userList.split('\n')
    textomsg1 = ''
    if message['chat']['username']:
        textomsg1 += message["chat"]["username"]
        with open('logs.log', 'a') as arquivo:
            arquivo.write('\n' + message["chat"]["username"] + '\n\n')
        if textomsg1 in user:
            await Form.apresentação.set()
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
            markup.add("Sim")
            markup.add("Não")
            await message.reply("Antes de começar, siga as regras para encontrar o nome:\n"
                                "1 - O nome não deve conter números.\n"
                                "2 - Escreva somente o primeiro nome.\n"
                                "3 - O nome não deve conter pontos, acentos ou traços.\n"
                                "Você concorda com as regras acima?", reply_markup=markup)
        else:
            await message.answer(
                "Olá, eu sou o Bot IBGE, criado para encontrar as informações do seu nome ou de outra pessoa.\n"
                "No momento você não possui permissão para acessar as informações internas.\n"
                "Entre em contato com os desenvolvedores.\n"
                "Para mais informações do meu criador digite '/info'")
    else:
        await message.answer('Olá ' + message['chat'][
            'first_name'] + ', no momento não encontrei seu username. Você deve verifica-lo nas configurações do Telegram.')


@dp.message_handler()
async def echo(message: types.Message, state: FSMContext):
    await types.ChatActions.typing(0.3)
    entradas = ['oi', 'olá', 'ola', 'oie', 'hey', 'eai', 'eae', 'hello', 'ei', 'hi', 'oii', 'oiee', 'ou']
    if message.text.lower() in (entradas):
        await message.answer('Olá ' + message['chat']['first_name'] + ', sou o Bot IBGE. Criado para encontrar as informações do seu nome ou de outra pessoa (nomes masculinos).\n'
                        'Você deve me fornecer um valor para pesquisa.')
    if message.text != '':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add("/start")
        await message.reply("Para iniciar minhas configurações você deve pressionar o botão '/start'.", reply_markup=markup)


# You can use state '*' if you need to handle all states
@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.next()
    # And remove keyboard (just in case)
    await message.reply('Cancelled.', reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(state=Form.apresentação)
async def process_name(message: types.Message, state: FSMContext):
    await types.ChatActions.typing(0.3)
    """
    Process user name
    """
    async with state.proxy() as data:
        data['apresentacao'] = message.text.lower()
    if data['apresentacao'] == 'não' or data['apresentacao'] == 'nao':
        await message.reply('Quando quiser, estou a dispósição!')
        await state.finish()
    elif data['apresentacao'] == 'sim' or data['apresentacao'] == 's':
        await Form.next()
        markup = types.ReplyKeyboardRemove()
        await message.reply("Qual nome você quer pesquisar?", reply_markup=markup)


# Check age. Age gotta be digit
@dp.message_handler(lambda message: message.text.isdigit(), state=Form.nome)
async def process_age_invalid(message: types.Message):
    return await message.reply("Você deve fornecer um nome.\n"
                               "Qual nome você quer pesquisar? (Digite novamente)")


@dp.message_handler(lambda message: message.text, state=Form.nome)
async def process_age(message: types.Message, state: FSMContext):
    # Update state and data
    await Form.next()
    await state.update_data(nome=(message.text.upper()))
    # Configure ReplyKeyboardMarkup
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("Frequência Masculina", "Frequência Feminina")
    markup.add("Gênero", "Frequência Total")
    markup.add("Explique os conceitos")
    await message.reply("Qual informação você deseja?", reply_markup=markup)



@dp.message_handler(lambda message: message.text not in ["Frequência Masculina", "Frequência Feminina", "Gênero", "Frequência Total","Explique os conceitos"], state=Form.info)
async def process_info_invalid(message: types.Message):
    """
    In this example gender has to be one of: Male, Female, Other.
    """
    return await message.reply("Você deve fornecer um valor válido no teclado criado.")


@dp.message_handler(state=Form.info)
async def process_info(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['info'] = message.text
        segundos = message['date']
        with open('logs.log', 'a') as arquivo:
            arquivo.write(segundos.__str__())

        with open('user.txt') as file:
            userList = file.read()
        # print(userList)

        user = userList.split('\n')
        # print(user)
        textomsg = ''
        if message["chat"]["username"]:
            textomsg += message["chat"]["username"]
            with open('logs.log', 'a') as arquivo:
                arquivo.write('\n' + message["chat"]["username"] + '\n\n')
        else:
            await message.answer("Você não possui um Username. Logo, deverá ir em suas configurações e nomea-lo.")

        if data['info'] == "Explique os conceitos":
            await types.ChatActions.typing(0.2)
            await message.answer('Gênero: Fornecerei o gênero que o IBGE reconhece o nome.')
            await types.ChatActions.typing(0.2)
            await message.answer('Frequência Masculina: Fornecerei o número de homens que possuem o nome pesquisado.')
            await types.ChatActions.typing(0.2)
            await message.answer('Frequência Feminina: Fornecerei o número de mulheres que possuem o nome pesquisado.')
            await types.ChatActions.typing(0.2)
            await message.answer('Frequência Total: Fornecerei o número total de pessoas que possuem o nome pesquisado.')
            await types.ChatActions.typing(2)
            await message.answer(f'<i><b>Clique na opção desejada.</b> </i>', parse_mode=types.ParseMode.HTML)
            return
        elif textomsg in user:
            txt = ''
            full
            for teste in full:
                if data['nome'] in teste['nome']:
                    txt += ('<b>Identifiquei.</>\n')
                    if data['info'] == "Gênero":
                        if teste['genero']:
                            txt += f'\n<b>Gênero:</b> <i>\n{teste["genero"]}</i>\n'
                    if data['info'] == "Frequência Feminina":
                        if teste['frequnciaF']:
                            txt += f'\n<b>Frequência Feminina:</b> <i>\n{teste["frequnciaF"]}</i>\n'
                    if data['info'] == "Frequência Masculina":
                        if teste['frequnciaM']:
                            txt += f'\n<b>Frequência Masculina:</b> <i>\n{teste["frequnciaM"]}</i>\n'
                    if data['info'] == "Frequência Total":
                        if teste['frequnciaT']:
                            txt += f'\n<b>Frequência Total:</b> <i>\n{teste["frequnciaT"]}</i>\n'

            if txt != '':
                await types.ChatActions.typing(0.3)
                await message.answer(txt, parse_mode=types.ParseMode.HTML)
            elif message.text.isdigit() == False:
                await message.answer('Nome não encontrado na base de dados.')
        # Remove keyboard
        markup = types.ReplyKeyboardRemove()

        # And send message
        if data['info'] != 'Explique os conceitos':
            await types.ChatActions.typing(0.3)
            await bot.send_message(
                message.chat.id,
                md.text(
                    md.text('Nome: ', md.bold(data['nome'])),
                    md.text('Informação pesquisada: ', data['info']),
                    sep='\n',
                ),
                reply_markup=markup,
                parse_mode=ParseMode.MARKDOWN,
            )

    # Finish conversation
    await state.finish()






if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
