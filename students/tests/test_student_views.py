"""Tests for students_list views"""
from datetime import datetime

from django.test import TestCase, Client, override_settings
from django.core.urlresolvers import reverse

from students.models import Student, Group


class TestStudentList(TestCase):

    def setUp(self):
        # create groups
        group1, created = Group.objects.get_or_create(
            title='MtM-1')
        group2, created = Group.objects.get_or_create(
            title='MtM-2')
        Student.objects.get_or_create(
            first_name="f_name1",
            last_name="l_name1",
            birthday=datetime.today(),
            ticket='1',
            student_group=group1)
        Student.objects.get_or_create(
            first_name="f_name2",
            last_name="l_name2",
            birthday=datetime.today(),
            ticket='2',
            student_group=group2)
        Student.objects.get_or_create(
            first_name="f_name3",
            last_name="l_name3",
            birthday=datetime.today(),
            ticket='3',
            student_group=group2)
        Student.objects.get_or_create(
            first_name="f_name4",
            last_name="l_name4",
            birthday=datetime.today(),
            ticket='4',
            student_group=group2)

        # remember test browser
        self.client = Client()

        self.url = reverse('home')

    def test_students_list(self):
        # make request to the server to get homepage page
        response = self.client.get(self.url)

        # do we have OK status from the server?
        self.assertEqual(response.status_code, 200)

        # do we have student name on a page?
        self.assertIn('f_name1', response.content)

        # do we have link to student edit form?
        self.assertIn(reverse('students_edit',
                              kwargs={'pk': Student.objects.all()[0].id}),
                      response.content)

        # ensure we got 3 students, pagination limit is 3
        self.assertEqual(len(response.context['students']), 3)

    def test_current_group(self):
        # set group as currently selected group
        group = Group.objects.filter(title='MtM-1')[0]
        self.client.cookies['current_group'] = group.id

        # make request to the server to get homepage page
        response = self.client.get(self.url)

        # in group1 we have only 1 student
        self.assertEqual(len(response.context['students']), 1)

    def test_order_by(self):
        # set order by Last Name
        response = self.client.get(self.url, {'order_by': 'last_name'})

        # now check if we got proper order
        students = response.context['students']
        self.assertEqual(students[0].last_name, 'l_name1')
        self.assertEqual(students[1].last_name, 'l_name2')
        self.assertEqual(students[2].last_name, 'l_name3')

    def test_reverse_order(self):
        response = self.client.get(self.url,
                                   {'order_by': 'last_name',
                                    'reverse': '1'})
        students = response.context['students']
        self.assertEqual(students[0].last_name, 'l_name4')
        self.assertEqual(students[1].last_name, 'l_name3')
        self.assertEqual(students[2].last_name, 'l_name2')

    def test_pagination(self):
        response = self.client.get(self.url,
                                   {'order_by': 'last_name',
                                    'reverse': '1',
                                    'page': '2'})
        students = response.context['students']
        self.assertEqual(students[0].last_name, 'l_name1')


@override_settings(LANGUAGE_CODE='en')
class TestStudentsDelete(TestCase):

    fixtures = ['students_test_data.json']

    def setUp(self):
        self.client = Client()
        self.url = reverse('students_delete', kwargs={'pk': 1})
        self.url_del_bunch = reverse('students_delete_bunch')


    def test_students_delete(self):
        self.client.login(username='admin', password='admin')

        # test get request
        response = self.client.get(self.url, follow=True)
        self.assertIn('Do you really want to delete student',
                      response.content)
        self.assertIn('action="%s"' % self.url, response.content)
        self.assertIn('name="delete_button"', response.content)

        # test post request
        response = self.client.post(self.url, follow=True)
        self.assertEqual(len(Student.objects.filter(id=1)), 0)
        self.assertIn('Student successfully deleted!', response.content)
        self.assertEqual(response.redirect_chain[0][0],
                         'http://testserver/')

    def test_students_delete_bunch(self):
        self.client.login(username='admin', password='admin')
        response = self.client.post(self.url_del_bunch,
                                    {'selected-student':1}, follow=True)

        # check response content
        self.assertIn('Selected students successfully deleted!',
                      response.content)
        # check if students deleted
        students = Student.objects.filter(id=1)
        self.assertEqual(len(students), 0)

        # check correct redirection
        self.assertEqual(response.redirect_chain[0][0],
                         'http://testserver/')



