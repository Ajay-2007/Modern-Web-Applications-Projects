from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import (TemplateView, FormView,
                                 CreateView, ListView,
                                 DetailView, UpdateView,
                                 DeleteView)

from classroom.forms import ContactForm
from .models import Teacher

# Create your views here.
def home_view(request):
    return render(request, 'classroom/home.html')

class HomeView(TemplateView):
    template_name = 'classroom/home.html'

class ThankYouView(TemplateView):
    template_name = 'classroom/thank_you.html'


# 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
class TeacherCreateView(CreateView):
    model = Teacher
    # model_form.html
    fields = "__all__"
    success_url = reverse_lazy('classroom:thank_you')


class ContactFormView(FormView):
    form_class = ContactForm
    template_name = 'classroom/contact.html'

    # success URL?
    # URL NOT a template.html
    # success_url = "/classroom/thank_you/" 
    success_url = reverse_lazy('classroom:thank_you')

    # what to do with form?
    def form_valid(self, form):
        print(form.cleaned_data['name'])
        #   ContactForm(request.POST)
        # form.save()
        return super().form_valid(form)

class TeacherListView(ListView):
    model = Teacher
    queryset = Teacher.objects.order_by('first_name')

    context_object_name = "teacher_list"

class TeacherDetailView(DetailView):
    # RETURN ONLY ONE MODEL ENTRY PK
    # model_detail.html
    model = Teacher
    # PK --> {{ teacher }}

class TeacherUpdateView(UpdateView):
    # SHARE model_form.html --- PK
    model = Teacher
    fields = "__all__"
    success_url = reverse_lazy('classroom:list_teacher')


class TeacherDeleteView(DeleteView):
    # Form --> Confirm Delete Button
    # default template name:
    # model_confirm_delete.html
    model = Teacher
    success_url = reverse_lazy('classroom:list_teacher')