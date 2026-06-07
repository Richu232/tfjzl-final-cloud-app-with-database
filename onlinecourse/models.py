import sys
from django.utils.timezone import now
try:
    from django.db import models
except Exception:
    print("There was an error loading django modules. Do you have django installed?")
    sys.exit()

from django.conf import settings

# Existing models like Course, Lesson, Enrollment, etc. remain unchanged here...

# --- NEW MODELS FOR TASK 1 ---

class Question(models.Model):
    # Foreign key link to Course (Many-to-One)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    # Question text text field
    question_text = models.CharField(max_length=500)
    # Grade point value for the question
    grade = models.IntegerField(default=5)

    def __str__(self):
        return self.question_text

    # Provided method to calculate if the learner answers correctly
    def is_get_score(self, selected_ids):
        all_answers = self.choice_set.filter(is_correct=True).count()
        selected_correct = self.choice_set.filter(is_correct=True, id__in=selected_ids).count()
        if all_answers == selected_correct:
            return True
        else:
            return False


class Choice(models.Model):
    # Foreign key link to Question (Many-to-One)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    # Choice content text field
    choice_text = models.CharField(max_length=500)
    # Boolean flag determining if the choice is a correct answer
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.choice_text


class Submission(models.Model):
    # Foreign key link to Enrollment (Many-to-One)
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    # Many-to-Many relationship with Choice model
    choices = models.ManyToManyField(Choice)

    def __str__(self):
        return "Submission " + str(self.id) + " for " + self.enrollment.user.username
