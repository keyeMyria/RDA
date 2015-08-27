from modules.builtin.models import PopupModule
from django.conf import settings
import os
from modules.exceptions import ModuleError
import json

RESOURCES_PATH = os.path.join(settings.SITE_ROOT, 'modules/diffusion/resources/')


class PeriodicTableModule(PopupModule):
    
    def __init__(self):
        with open(RESOURCES_PATH + 'html/periodic.html', 'r') as periodic_file:        
            periodic_table = periodic_file.read()

        PopupModule.__init__(self, popup_content=periodic_table, button_label='Select Element',
                             styles=[os.path.join(RESOURCES_PATH, 'css/periodic.css')],
                             scripts=[os.path.join(RESOURCES_PATH, 'js/periodic.js')])

    def _get_module(self, request):
        return PopupModule.get_module(self, request)

    def _get_display(self, request):
        return 'No element selected'

    def _get_result(self, request):
        return ''

    def _is_data_valid(self, data):
        return True

    def _post_display(self, request):
        if 'selectedElement' not in request.POST:
            return self._get_display(request)
        else:
            return 'Chosen element: ' + request.POST['selectedElement']

    def _post_result(self, request):
        if 'selectedElement' not in request.POST:
            return self._get_result(request)

        return request.POST['selectedElement']


class PeriodicTableMultipleModule(PopupModule):

    def __init__(self):
        with open(RESOURCES_PATH + 'html/periodic_multiple.html', 'r') as periodic_file:
            periodic_table = periodic_file.read()

        PopupModule.__init__(self, popup_content=periodic_table, button_label='Select Elements',
                             styles=[os.path.join(RESOURCES_PATH, 'css/periodic.css'),
                                     os.path.join(RESOURCES_PATH, 'css/periodic_multiple.css')],
                             scripts=[os.path.join(RESOURCES_PATH, 'js/periodic_multiple.js')])

    def _get_module(self, request):
        return PopupModule.get_module(self, request)

    def _get_display(self, request):
        return 'No elements selected'

    def _get_result(self, request):
        return ''

    def _is_data_valid(self, data):
        return True

    def _post_display(self, request):
        if 'elementList' in request.POST:
            element_list = json.loads(request.POST['elementList'])

            if len(element_list) == 0:
                element_list_disp = self._get_display(request)
            else:
                element_list_disp = '<table class="table table-striped element-list">'
                element_list_disp += '<thead><tr>'
                element_list_disp += '<th>Element</th>'
                element_list_disp += '<th>Quantity</th>'
                element_list_disp += '<th>Purity</th>'
                element_list_disp += '<th>Error</th>'
                element_list_disp += '</tr></thead>'
                element_list_disp += '<tbody>'

                for element in element_list:
                    element_list_disp += '<tr>'
                    element_list_disp += "<td>" + element['name'] + "</td>"
                    element_list_disp += "<td>" + element['qty'] + "</td>"
                    element_list_disp += "<td>" + element['pur'] + "</td>"
                    element_list_disp += "<td>" + element['err'] + "</td>"
                    element_list_disp += '</tr>'

                element_list_disp += '</tbody>'
                element_list_disp += '</table>'

            return element_list_disp
        else:
            return self._get_display(request)

    def _post_result(self, request):
        if 'elementList' in request.POST:
            element_list = json.loads(request.POST['elementList'])

            if len(element_list) == 0:
                element_list_xml = self._get_result(request)
            else:
                element_list_xml = ""

                for element in element_list:
                    element_list_xml += '<constituent>'
                    element_list_xml += "<element>" + element['name'] + "</element>"
                    element_list_xml += "<quantity>" + element['qty'] + "</quantity>"
                    element_list_xml += "<purity>" + element['pur'] + "</purity>"
                    element_list_xml += "<error>" + element['err'] + "</error>"
                    element_list_xml += '</constituent>'

            return element_list_xml
        else:
            return self._get_result(request)

    # def get_default_display(self, request):
    #     return "No elements selected"
    #
    # def get_default_result(self, request):
    #     return ""

    # def process_data(self, request):
    #     if 'elementList' in request.POST:
    #         element_list = json.loads(request.POST['elementList'])
    #
    #         if len(element_list) == 0:
    #             element_list_disp = self.get_default_display(request)
    #             element_list_xml = ""
    #         else:
    #             element_list_disp = '<table class="table table-striped element-list">'
    #             element_list_disp += '<thead><tr>'
    #             element_list_disp += '<th>Element</th>'
    #             element_list_disp += '<th>Quantity</th>'
    #             element_list_disp += '<th>Purity</th>'
    #             element_list_disp += '<th>Error</th>'
    #             element_list_disp += '</tr></thead>'
    #             element_list_disp += '<tbody>'
    #
    #             element_list_xml = ""
    #
    #             for element in element_list:
    #                 element_list_xml += '<constituent>'
    #                 element_list_xml += "<element>" + element['name'] + "</element>"
    #                 element_list_xml += "<quantity>" + element['qty'] + "</quantity>"
    #                 element_list_xml += "<purity>" + element['pur'] + "</purity>"
    #                 element_list_xml += "<error>" + element['err'] + "</error>"
    #                 element_list_xml += '</constituent>'
    #
    #                 element_list_disp += '<tr>'
    #                 element_list_disp += "<td>" + element['name'] + "</td>"
    #                 element_list_disp += "<td>" + element['qty'] + "</td>"
    #                 element_list_disp += "<td>" + element['pur'] + "</td>"
    #                 element_list_disp += "<td>" + element['err'] + "</td>"
    #                 element_list_disp += '</tr>'
    #
    #             element_list_disp += '</tbody>'
    #             element_list_disp += '</table>'
    #
    #         return element_list_disp, element_list_xml
    #     else:
    #         raise ModuleError('Selected Element not properly sent to server. '
    #                           'Please set "selectedElement" in POST data.')
