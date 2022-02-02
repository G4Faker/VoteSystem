from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import VoteModel, CandidateModel, VoiceUser, HashVoiceUser
from py_paillier import py_paillier as paillier
from django.contrib.auth.models import User
# Create your views here.


# отрисовка всех карточек голосования
class VotesView(ListView):
    model = VoteModel
    context_object_name = 'votes_list'
    template_name = 'vote-cards.html'

    # расширить доступные переменные и записи из БД
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['candidates_list'] = CandidateModel.objects.all()
        return context


# отрисовка начавшихся карточек голосования
class RunningVotesView(ListView):
    model = VoteModel
    context_object_name = 'votes_list'
    template_name = 'running-vote-cards.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['candidates_list'] = CandidateModel.objects.all()
        context['running_votes'] = VoteModel.objects.filter(start=True).filter(complete=False)
        return context


# отрисовка законченных карточек голосования
class CompletesVotesView(ListView):
    model = VoteModel
    context_object_name = 'votes_list'
    template_name = 'complete-vote-cards.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['candidates_list'] = CandidateModel.objects.all()
        context['completes_votes'] = VoteModel.objects.filter(start=True).filter(complete=True)
        return context


# отрисовка не начатах карточек голосования
class DontStartsVotesView(ListView):
    model = VoteModel
    context_object_name = 'votes_list'
    template_name = 'dont-start-vote-cards.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['candidates_list'] = CandidateModel.objects.all()
        context['dont_starts_votes'] = VoteModel.objects.filter(start=False).filter(complete=False)
        return context


# отрисовка голосования в деталях
class VoteDetailView(DetailView):
    model = VoteModel
    context_object_name = 'vote'
    template_name = 'vote-detail.html'

    # расширение контекста
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # добавлене списка кандидатов в данном голосовании
        candidates_list = CandidateModel.objects.filter(vote=context['object'])
        # список голосов пользователей
        users_voices = VoiceUser.objects.filter(vote=context['object'])

        context['candidates_list'] = candidates_list
        context['users_voices'] = users_voices
        return context


# начало голосования
def start_vote(request):
    # считываем данные из запроса
    data = request.POST
    # получаем id голосования из данных запроса
    vote_id = int(data['vote-id'])
    # получаем голосование по его id
    vote = VoteModel.objects.get(pk=vote_id)

    # устанавливаем флаг начала голосования
    vote.start = True

    # генерация ключей
    public_key: paillier.PaillierPublicKey
    private_key: paillier.PaillierPrivateKey

    public_key, private_key, p, q = paillier.PaillierKeyPairGenerator().paillier_key_pair_generation(
        bit_key_length=32,
        return_pq=True
    )

    # запись ключей
    vote.public_key = f'{public_key.n}, {public_key.g}'
    vote.private_key = f'{private_key.lambdas}, {private_key.mu}'

    vote.p = p
    vote.q = q

    # сохранение измененной записи в БД
    vote.save()

    # возврат на страницу начала голосования
    return render(request, 'start-vote.html')


# завершение голосования
def complete_vote(request):
    # считываем данные из запроса
    data = request.POST
    # получаем id голосования из данных запроса
    vote_id = int(data['vote-id'])
    # получаем голосование по его id
    vote = VoteModel.objects.get(pk=vote_id)

    # устанавливаем флаг окончания голосования
    vote.complete = True

    # подсчет голосов

    # генерируем ключи как объекты классов
    public_key: paillier.PaillierPublicKey
    private_key: paillier.PaillierPrivateKey

    public_key, private_key = paillier.PaillierKeyPairGenerator().paillier_key_pair_generation(
        bit_key_length=32
    )

    # получем из голосования данные открытого ключа
    words_public_key = vote.public_key.split(', ')

    # переводим строки в числа
    digit_public_key = [int(word) for word in words_public_key]

    # меняем значения в созданном объекте на данные откртыго ключа по голосанию
    public_key.n = digit_public_key[0]
    public_key.g = digit_public_key[1]
    public_key.n_square = digit_public_key[0] ** 2

    # создание приватного ключа
    private_key = paillier.PaillierPrivateKey(
        public_key, int(vote.p), int(vote.q)
    )

    # получение голосов пользователей по id голосования
    users_voices = VoiceUser.objects.filter(vote=vote.id)

    # получаем данные голоса из объектов
    users_voices_list = []
    for users_voice in users_voices:
        users_voices_list.append(users_voice.voice)

    # вычисление результата голосования
    # перемножение зашифрованных голосов избирателей
    vote_result_encrypt = 1

    for user_voice in users_voices_list:
        vote_result_encrypt = (vote_result_encrypt * user_voice) % public_key.n_square

    # расшифрование результата голосования
    vote_result = private_key.decryption([vote_result_encrypt])[0]

    # переворачиваем последовательность голосов
    candidates_res_votes = []
    m = vote_result
    while m > 0:
        r = m % 10
        candidates_res_votes.append(r)
        m = m - r
        m = int(m / 10)

    # получаем список кандидатов по id голосования
    candidates_list = CandidateModel.objects.filter(vote=vote.id)
    # вычисляем максимальное значение голосов
    max_voices = max(candidates_res_votes)
    # определяем индекс максимального значения
    index_max_voices = candidates_res_votes.index(max_voices)
    # определяем победителя по индексу
    win_candidate = CandidateModel.objects.get(pk=candidates_list[index_max_voices].pk)

    # внесение изменений в запись голосования и сохранение в БД
    vote.candidate = win_candidate.name
    vote.save()
    # возврат на страницу окончания голосования
    return render(request, 'complete-vote.html')


# пользователь отдает свой голос
def user_voted(request):
    # считываем данные из запроса
    data = request.POST
    # получаем id голосования из данных запроса
    vote_id = int(data['vote-id'])
    # получаем голосование по его id
    vote = VoteModel.objects.get(pk=vote_id)
    # получаем id пользователя из данных запроса
    user_id = int(data['user-id'])
    # получаем пользователя по его id
    user = User.objects.get(pk=user_id)

    # генерируем открытый ключ как объект класса
    public_key: paillier.PaillierPublicKey
    public_key, private_key = paillier.PaillierKeyPairGenerator().paillier_key_pair_generation(
        bit_key_length=32
    )

    # получем из голосования данные открытого ключа
    words_public_key = vote.public_key.split(', ')
    # переводим символы в числа
    digit_public_key = [int(word) for word in words_public_key]
    # меняем значения в созданном объекте на данные открытого ключа по голосованию
    public_key.n = digit_public_key[0]
    public_key.g = digit_public_key[1]
    public_key.n_square = digit_public_key[0] ** 2

    # получаем значение кандидата из данных запроса
    candidate_value = int(data['candidate-value'])
    # шифрование голоса избирателя
    user_vote = public_key.encryption([candidate_value])[0]

    # создание записи "голос-пользователя" в БД
    voice_user = VoiceUser(
        vote=vote,
        voice=user_vote,
        user=user
    )
    # сохранение созданной записи
    voice_user.save()

    # вычисление хеша
    hash_voice_user = HashVoiceUser(
        voice_hash=voice_user.get_hash(),
        voice=voice_user
    )
    # сохранение записи хеша
    hash_voice_user.save()

    # возврат на страницу "ваш голос отдан"
    return render(request, 'user-voted.html')


# проверка целостности
def integrity_control(request):
    # считываем данные из запроса
    data = request.POST
    # получаем id голосования из данных запроса
    vote_id = int(data['vote-id'])
    # получаем голосование по его id
    vote = VoteModel.objects.get(pk=vote_id)

    # получаем голоса пользователей по голосованию
    users_voices = VoiceUser.objects.filter(vote=vote)

    # выполняем проверку целостности
    integrity = True

    for user_voice in users_voices:
        integrity = integrity and HashVoiceUser.objects.filter(voice=user_voice)[0].integrity_control()
    # если целостность сохранена выполнить возврат на страницу "целостность данных не нарушена"
    if integrity:
        return render(request, 'integrity-control-true.html')
    # если целостность не сохранена выполнить возврат на страницу "целостность данных нарушена"
    else:
        return render(request, 'integrity-control-false.html')
