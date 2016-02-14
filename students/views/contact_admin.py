# -*- coding: utf-8 -*-
# writed as in the book of V.Podoba
from django.shortcuts import render, redirect
from django import forms
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.views.generic import FormView

from studentsdb.settings import ADMIN_EMAIL

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class ContactAdminForm(forms.Form):
    def __init__(self, *args, **kwargs):
        # call original initialiazator
        super(ContactAdminForm, self).__init__(*args, **kwargs)

        # this helper object allows us to customize form
        self.helper = FormHelper()

        # form tag attributes
        self.helper.form_class = 'form-horizontal'
        self.helper.form_method = 'post'
        #self.helper.form_action = reverse('contact_admin')

        # twitter bootstrap styles
        self.helper.help_text_inline = True
        self.helper.html5_required = True
        self.helper.label_class = 'col-sm-2 control-label'
        self.helper.field_class = 'col-sm-10 form-field-width'

        # form buttons
        self.helper.add_input(Submit('send_button', u'Надіслати'))

    from_email = forms.EmailField(
        label=u"Ваша Емейл Адреса")

    subject = forms.CharField(
        label=u"Заголовок Листа",
        max_length=128)

    message = forms.CharField(
        label=u"Текст повідомлення",
        max_length=2500,
        widget=forms.Textarea)

    recipient_list = [ADMIN_EMAIL]

    def send_email(self):
        send_mail(**self.cleaned_data)
        


class ContactAdminView(FormView):
    form_class = ContactAdminForm
    template_name = 'contact_admin/form.html'

    def get_success_url(self):
        return reverse('contact_admin')

    def form_valid(self, form):
        try:
            form.send_email()
        except Exception:
            messages.info(self.request, u"Сталася якась помилка, лист не відправився. Shit happens :)")
        else:
            messages.info(self.request, u"Лист відправлено. Верховна канцелярія вже займається обробкою!")
        return super(ContactAdminView, self).form_valid(form)



'''
def contact_admin(request):
    # check if form was posted
    if request.method == 'POST':
        # create a form instance and populate it
        # with data from the request
        form = ContactAdminForm(request.POST)

        # check whether user data is valid:
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            from_email = form.cleaned_data['from_email']
            try:
                send_mail(subject, from_email+'\n\n'+message, from_email, [ADMIN_EMAIL])
            except Exception:
                messages.info(
                    request,
                    u"""Під час віправки листа виникла непередабачувана помилка.
                    Спробуйте скористатися данною формою пізніше.""")
            else:
                messages.info(request, u"Повідомлення успішно надіслане")

            # redirect to same contact page with messages
            return HttpResponseRedirect(reverse('contact_admin'))

    # if there was not POST render blank form
    else:
        context = { 'form': ContactAdminForm()}

    return render(request, 'contact_admin/form.html', context)
'''
