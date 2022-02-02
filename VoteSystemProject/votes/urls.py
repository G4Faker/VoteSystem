from django.urls import path
from .views import *


urlpatterns = [
    # все
    path('all', VotesView.as_view(), name='votes'),
    # идущие
    path('running', RunningVotesView.as_view(), name='run-votes'),
    # завершенные
    path('complete', CompletesVotesView.as_view(), name='complete-votes'),
    # не начатые
    path('not-start', DontStartsVotesView.as_view(), name='dont-run-votes'),
    path('vote/<int:pk>', VoteDetailView.as_view(), name='vote-detail'),
    path('start-vote', start_vote, name='start_vote'),
    path('complete-vote', complete_vote, name='complete_vote'),
    path('integrity-control', integrity_control, name='integrity_control'),
    path('user-voted', user_voted, name='user_voted'),
]
