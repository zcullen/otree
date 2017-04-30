from otree.api import Currency as c, currency_range, safe_json
from . import models
from ._builtin import Page, WaitPage
from .models import Constants, levenshtein, distance_and_ok
from django.conf import settings



class Introduction(Page):       # both
    def is_displayed(self):
        self.round_number == 1
    timeout_seconds = 60
    form_model = models.Player
    form_fields = ['devSkip']
 #   pass

class Manager_Introduction(Page):   # extra manager intro
    timeout_seconds = 60
    def is_displayed(self):
        if ( self.player.id_in_group == 1 ) & ( self.player.devSkip == None ):
            return True

class AcceptTerms(Page):        # both
    timeout_seconds = 180
    def is_displayed(self):
        if ( self.player.devSkip == None ):
            return True
    form_model = models.Player
    form_fields = ['MTurkID', 'paymentOK', 'neverWorked', 'yearBorn', 'gender']

class SurveyManager(Page):      # survey for manager
    timeout_seconds = 120
    def is_displayed(self):
        if ( self.player.id_in_group == 1 ) & ( self.player.devSkip == None ):
            return True
    form_model = models.Player
    form_fields = ['experience', 'eduLevel', 'dailyHHEarn']

class SurveyEmployee(Page):     # survey for employee
    timeout_seconds = 120
    def is_displayed(self):
        if ( self.player.id_in_group != 1 ) & ( self.player.devSkip == None ):
            return True
    form_model = models.Player
    form_fields = ['transExp', 'eduLevel', 'dailyHHEarn']

class SampleManager(Page):      # transcription sample for manager
    def is_displayed(self):
        if ( self.player.id_in_group == 1 ) & ( self.player.devSkip == None ):
            return True
    timeout_seconds = 120
    pass
 
class SampleEmployee(Page):     #transcription sample for employee with time estimate
    def is_displayed(self):
        if ( self.player.id_in_group != 1 ) & ( self.player.devSkip == None ):
            return True
    timeout_seconds = 120
    form_model = models.Player
    form_fields = ['howLong']

class PreferencesEmployee(Page):    # preferences survey for eployee
    def is_displayed(self):
        if ( self.player.id_in_group != 1 ) & ( self.player.devSkip == None ):
            return True
    timeout_seconds = 180
    form_model = models.Player
    form_fields = ['pref1','pref2','pref3','pref4','pref5']

class BidManager(Page):             # bid for manager
    def is_displayed(self):
        if ( self.player.id_in_group == 1 ) & ( self.player.devSkip == None ):
            return True
    timeout_seconds = 180
    pass

class BidEmployee(Page):        # bid for employee
    def is_displayed(self):
        if ( self.player.id_in_group != 1 ) & ( self.player.devSkip == None ):
            return True
    timeout_seconds = 180
    form_model = models.Player
    form_fields = ['bid']

class PreChatManager(Page):
    def is_displayed(self):
        if ( self.player.id_in_group == 1 ) & ( self.player.devSkip == None ):
            return True
    timeout_seconds = 300
    pass

class PreChatEmployee(Page):
    def is_displayed(self):
        if ( self.player.id_in_group != 1 ) & ( self.player.devSkip == None ):
            return True
    timeout_seconds = 300
    pass

class ManagerChat(Page):
    def is_displayed(self):
        if ( self.player.id_in_group == 1 ):
            return True
#    timeout_seconds = 1800
    pass

class EmployeeChat(Page):
    def is_displayed(self):
        if ( self.player.id_in_group != 1 ):
            return True
#    timeout_seconds = 1800
    pass

#    form_fields = ['experience', 'transExp']

class ResultsWaitPage(WaitPage):
#    def is_displayed(self):
#        return self.player.id_in_group == 1
    def after_all_players_arrive(self):
        pass

class Transcribe(Page):
    form_model = models.Player
    form_fields = ['transcribed_text']

    def vars_for_template(self):

        return {
            'image_path': 'transcription/paragraphs/{}_{}.png'.format(self.player.id_in_group,
                self.round_number),
            'reference_text': safe_json(Constants.reference_texts[self.round_number - 1]),
            'debug': settings.DEBUG,
            'required_accuracy': 100 * (1 - Constants.allowed_error_rates[self.round_number - 1])
        }

    def transcribed_text_error_message(self, transcribed_text):
        reference_text = Constants.reference_texts[self.round_number - 1]
        allowed_error_rate = Constants.allowed_error_rates[
            self.round_number - 1]
        distance, ok = distance_and_ok(transcribed_text, reference_text,
                                       allowed_error_rate)
        if ok:
            self.player.levenshtein_distance = distance
        else:
            if allowed_error_rate == 0:
                return "The transcription should be exactly the same as on the image."
            else:
                return "This transcription appears to contain too many errors."

    def before_next_page(self):
        self.player.payoff = 0

class Results(Page):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds

    def vars_for_template(self):
        table_rows = []
        for prev_player in self.player.in_all_rounds():
            row = {
                'round_number': prev_player.round_number,
                'reference_text_length': len(Constants.reference_texts[prev_player.round_number - 1]),
                'transcribed_text_length': len(prev_player.transcribed_text),
                'distance': prev_player.levenshtein_distance,
            }
            table_rows.append(row)

        return {'table_rows': table_rows}


page_sequence = [Introduction, Transcribe, Results]
'''
page_sequence = [
	Introduction,
	Manager_Introduction,
    AcceptTerms,
    SurveyManager,
    SurveyEmployee,
    SampleManager,
    SampleEmployee,
    PreferencesEmployee,
    BidManager,
    BidEmployee,
    PreChatManager,
    PreChatEmployee,
    ResultsWaitPage,
    ManagerChat,
    EmployeeChat
]
'''