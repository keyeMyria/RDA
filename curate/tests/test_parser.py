"""
"""
from django.http.request import HttpRequest
from django.test import TestCase
from django.utils.importlib import import_module
from os.path import join
from curate.parser import remove_annotations, generate_choice, generate_restriction, \
    generate_simple_type, generate_extension, generate_simple_content, lookup_occurs, \
    manage_occurences, manage_attr_occurrences, has_module, get_xml_element_data, get_element_type, get_nodes_xpath, \
    generate_sequence, generate_element, generate_complex_type, generate_element_absent, generate_sequence_absent, \
    generate_form, generate_module
from mgi.models import Module, FormElement, FormData
from mgi.tests import DataHandler, are_equals
from lxml import etree


##################################################
# Part I: Utilities testing
##################################################

# class ParserGetSubnodesXPathTestSuite(TestCase):
#     """
#     """
#
#     def setUp(self):
#         subnodes_data = join('curate', 'tests', 'data', 'parser', 'utils', 'xpath')
#         self.subnodes_data_handler = DataHandler(subnodes_data)
#
#     def test_not_element(self):
#         not_element_xsd = self.subnodes_data_handler.get_xsd2('not_element')
#         xpath_result = get_subnodes_xpath(not_element_xsd, not_element_xsd, '')
#
#         self.assertEqual(xpath_result, [])
#
#     def test_imbricated_elements(self):
#         document = join('imbricated_elements', 'document')
#         imbricated_elements_xsd = self.subnodes_data_handler.get_xsd2(document)
#
#         child_0 = join('imbricated_elements', 'child_0')
#         imbricated_element_0_xsd = self.subnodes_data_handler.get_xsd2(child_0)
#
#         child_1 = join('imbricated_elements', 'child_1')
#         imbricated_element_1_xsd = self.subnodes_data_handler.get_xsd2(child_1)
#
#         child_2 = join('imbricated_elements', 'child_2')
#         imbricated_element_2_xsd = self.subnodes_data_handler.get_xsd2(child_2)
#
#         xpath_result = get_subnodes_xpath(imbricated_elements_xsd, imbricated_elements_xsd, '')
#         expected_result = [
#             {
#                 'name': 'child_0',
#                 'element': imbricated_element_0_xsd
#             },
#             {
#                 'name': 'child_1',
#                 'element': imbricated_element_1_xsd
#             },
#             {
#                 'name': 'child_2',
#                 'element': imbricated_element_2_xsd
#             },
#         ]
#
#         self.assertEqual(len(xpath_result), len(expected_result))
#
#         for xpath in xpath_result:
#             xpath_elem = xpath['element']
#
#             expected_elem_list = [expect['element'] for expect in expected_result if expect['name'] == xpath['name']]
#             expect_elem = expected_elem_list[0] if len(expected_elem_list) == 1 else None
#
#             self.assertTrue(are_equals(xpath_elem, expect_elem))
#
#     def test_element_has_name(self):
#         document = join('element_with_name', 'document')
#         named_element_xsd = self.subnodes_data_handler.get_xsd2(document)
#
#         child_0 = join('element_with_name', 'child_0')
#         child_0_xsd = self.subnodes_data_handler.get_xsd2(child_0)
#
#         child_1 = join('element_with_name', 'child_1')
#         child_1_xsd = self.subnodes_data_handler.get_xsd2(child_1)
#
#         xpath_result = get_subnodes_xpath(named_element_xsd, named_element_xsd, '')
#         expected_result = [
#             {
#                 'name': 'child_0',
#                 'element': child_0_xsd
#             },
#             {
#                 'name': 'child_1',
#                 'element': child_1_xsd
#             }
#         ]
#
#         self.assertEqual(len(xpath_result), len(expected_result))
#
#         for xpath in xpath_result:
#             xpath_elem = xpath['element']
#
#             expected_elem_list = [expect['element'] for expect in expected_result if expect['name'] == xpath['name']]
#             expect_elem = expected_elem_list[0] if len(expected_elem_list) == 1 else None
#
#             self.assertTrue(are_equals(xpath_elem, expect_elem))
#
#     def test_element_ref_has_namespace(self):
#         # FIXME This test should not work (see how to correct it)
#         document = join('element_with_ref_namespace', 'document')
#         ref_element_no_namespace_xsd = self.subnodes_data_handler.get_xsd2(document)
#
#         child_0 = join('element_with_ref_namespace', 'child_0')
#         child_0_xsd = self.subnodes_data_handler.get_xsd2(child_0)
#
#         ref_0 = join('element_with_ref_namespace', 'ref_0')
#         ref_0_xsd = self.subnodes_data_handler.get_xsd2(ref_0)
#
#         xpath_result = get_subnodes_xpath(ref_element_no_namespace_xsd, ref_element_no_namespace_xsd, '')
#
#         expected_result = [
#             {
#                 'name': 'child_0',
#                 'element': child_0_xsd
#             },
#             {
#                 'name': 'ref_0',
#                 'element': ref_0_xsd
#             },
#             {  # FIXME the 2nd element shouldn't be here (not needed)
#                 'name': 'ref_0',
#                 'element': ref_0_xsd
#             }
#         ]
#
#         self.assertEqual(len(xpath_result), len(expected_result))
#
#         for xpath in xpath_result:
#             xpath_elem = xpath['element']
#
#             expected_elem_list = [expect['element'] for expect in expected_result if expect['name'] == xpath['name']]
#             # FIXME Having 2 element with the same content is not useful (>= 1 should be replaced by == 1)
#             expect_elem = expected_elem_list[0] if len(expected_elem_list) >= 1 else None
#
#             self.assertTrue(are_equals(xpath_elem, expect_elem))
#
#     def test_element_ref_has_no_namespace(self):
#         document = join('element_with_ref_no_namespace', 'document')
#         ref_element_no_namespace_xsd = self.subnodes_data_handler.get_xsd2(document)
#
#         child_0 = join('element_with_ref_no_namespace', 'child_0')
#         child_0_xsd = self.subnodes_data_handler.get_xsd2(child_0)
#
#         ref_0 = join('element_with_ref_no_namespace', 'ref_0')
#         ref_0_xsd = self.subnodes_data_handler.get_xsd2(ref_0)
#
#         xpath_result = get_subnodes_xpath(ref_element_no_namespace_xsd, ref_element_no_namespace_xsd, '')
#
#         expected_result = [
#             {
#                 'name': 'child_0',
#                 'element': child_0_xsd
#             },
#             {
#                 'name': 'ref_0',
#                 'element': ref_0_xsd
#             },
#             {  # FIXME the 2nd element shouldn't be here (not needed)
#                 'name': 'ref_0',
#                 'element': ref_0_xsd
#             }
#         ]
#
#         self.assertEqual(len(xpath_result), len(expected_result))
#
#         for xpath in xpath_result:
#             xpath_elem = xpath['element']
#
#             expected_elem_list = [expect['element'] for expect in expected_result if expect['name'] == xpath['name']]
#             # FIXME Having 2 element with the same content is not useful (>= 1 should be replaced by == 1)
#             expect_elem = expected_elem_list[0] if len(expected_elem_list) >= 1 else None
#
#             self.assertTrue(are_equals(xpath_elem, expect_elem))


class ParserGetNodesXPathTestSuite(TestCase):
    """
    """

    def setUp(self):
        subnodes_data = join('curate', 'tests', 'data', 'parser', 'utils', 'xpath')
        self.subnodes_data_handler = DataHandler(subnodes_data)

    def test_not_element(self):
        not_element_xsd = self.subnodes_data_handler.get_xsd2('not_element')
        xpath_result = get_nodes_xpath(not_element_xsd, not_element_xsd, '')

        self.assertEqual(xpath_result, [])

    def test_imbricated_elements(self):
        document = join('imbricated_elements', 'document')
        imbricated_elements_xsd = self.subnodes_data_handler.get_xsd2(document)

        child_0 = join('imbricated_elements', 'child_0')
        imbricated_element_0_xsd = self.subnodes_data_handler.get_xsd2(child_0)

        child_1 = join('imbricated_elements', 'child_1')
        imbricated_element_1_xsd = self.subnodes_data_handler.get_xsd2(child_1)

        child_2 = join('imbricated_elements', 'child_2')
        imbricated_element_2_xsd = self.subnodes_data_handler.get_xsd2(child_2)

        xpath_result = get_nodes_xpath(imbricated_elements_xsd, imbricated_elements_xsd, '')
        expected_result = [
            {
                'name': 'child_0',
                'element': imbricated_element_0_xsd
            },
            {
                'name': 'child_1',
                'element': imbricated_element_1_xsd
            },
            {
                'name': 'child_2',
                'element': imbricated_element_2_xsd
            },
        ]

        self.assertEqual(len(xpath_result), len(expected_result))

        for xpath in xpath_result:
            xpath_elem = xpath['element']

            expected_elem_list = [expect['element'] for expect in expected_result if expect['name'] == xpath['name']]
            expect_elem = expected_elem_list[0] if len(expected_elem_list) == 1 else None

            self.assertTrue(are_equals(xpath_elem, expect_elem))

    def test_element_has_name(self):
        document = join('element_with_name', 'document')
        named_element_xsd = self.subnodes_data_handler.get_xsd2(document)

        child_0 = join('element_with_name', 'child_0')
        child_0_xsd = self.subnodes_data_handler.get_xsd2(child_0)

        child_1 = join('element_with_name', 'child_1')
        child_1_xsd = self.subnodes_data_handler.get_xsd2(child_1)

        xpath_result = get_nodes_xpath(named_element_xsd, named_element_xsd, '')
        expected_result = [
            {
                'name': 'child_0',
                'element': child_0_xsd
            },
            {
                'name': 'child_1',
                'element': child_1_xsd
            }
        ]

        self.assertEqual(len(xpath_result), len(expected_result))

        for xpath in xpath_result:
            xpath_elem = xpath['element']

            expected_elem_list = [expect['element'] for expect in expected_result if expect['name'] == xpath['name']]
            expect_elem = expected_elem_list[0] if len(expected_elem_list) == 1 else None

            self.assertTrue(are_equals(xpath_elem, expect_elem))

    def test_element_ref_has_namespace(self):
        # FIXME Correct the test for correct expected output
        document = join('element_with_ref_namespace', 'document')
        ref_element_no_namespace_xsd = self.subnodes_data_handler.get_xsd2(document)

        child_0 = join('element_with_ref_namespace', 'child_0')
        child_0_xsd = self.subnodes_data_handler.get_xsd2(child_0)

        ref_0 = join('element_with_ref_namespace', 'ref_0')
        ref_0_xsd = self.subnodes_data_handler.get_xsd2(ref_0)

        xpath_result = get_nodes_xpath(ref_element_no_namespace_xsd, ref_element_no_namespace_xsd, '')

        expected_result = [
            {
                'name': 'child_0',
                'element': child_0_xsd
            },
            {
                'name': 'ref_0',
                'element': ref_0_xsd
            },
            {  # FIXME the 2nd element shouldn't be here (not needed)
                'name': 'ref_0',
                'element': ref_0_xsd
            }
        ]

        self.assertEqual(len(xpath_result), len(expected_result))

        for xpath in xpath_result:
            # print xpath['name']
            # print etree.tostring(xpath['element'])
            xpath_elem = xpath['element']

            expected_elem_list = [expect['element'] for expect in expected_result if expect['name'] == xpath['name']]
            # FIXME Having 2 element with the same content is not useful (>= 1 should be replaced by == 1)
            expect_elem = expected_elem_list[0] if len(expected_elem_list) >= 1 else None

            self.assertTrue(are_equals(xpath_elem, expect_elem))

    def test_element_ref_has_no_namespace(self):
        document = join('element_with_ref_no_namespace', 'document')
        ref_element_no_namespace_xsd = self.subnodes_data_handler.get_xsd2(document)

        child_0 = join('element_with_ref_no_namespace', 'child_0')
        child_0_xsd = self.subnodes_data_handler.get_xsd2(child_0)

        ref_0 = join('element_with_ref_no_namespace', 'ref_0')
        ref_0_xsd = self.subnodes_data_handler.get_xsd2(ref_0)

        xpath_result = get_nodes_xpath(ref_element_no_namespace_xsd, ref_element_no_namespace_xsd, '')

        expected_result = [
            {
                'name': 'child_0',
                'element': child_0_xsd
            },
            {
                'name': 'ref_0',
                'element': ref_0_xsd
            },
            {  # FIXME the 2nd element shouldn't be here (not needed)
                'name': 'ref_0',
                'element': ref_0_xsd
            }
        ]

        self.assertEqual(len(xpath_result), len(expected_result))

        for xpath in xpath_result:
            xpath_elem = xpath['element']

            expected_elem_list = [expect['element'] for expect in expected_result if expect['name'] == xpath['name']]
            # FIXME Having 2 element with the same content is not useful (>= 1 should be replaced by == 1)
            expect_elem = expected_elem_list[0] if len(expected_elem_list) >= 1 else None

            self.assertTrue(are_equals(xpath_elem, expect_elem))


class ParserLookupOccursTestSuite(TestCase):
    """
    """

    def setUp(self):
        occurs_data = join('curate', 'tests', 'data', 'parser', 'utils', 'occurs')
        self.occurs_data_handler = DataHandler(occurs_data)

    def test_reload_compliant_element(self):
        lookup_xsd = self.occurs_data_handler.get_xsd2('document')
        compliant_xml = self.occurs_data_handler.get_xml('compliant')

        max_occurs_found = lookup_occurs(lookup_xsd, lookup_xsd, '', '.', compliant_xml)
        self.assertEqual(max_occurs_found, 1)

    def test_reload_noncompliant_element(self):
        lookup_xsd = self.occurs_data_handler.get_xsd2('document')
        noncompliant_xml = self.occurs_data_handler.get_xml('noncompliant')

        max_occurs_found = lookup_occurs(lookup_xsd, lookup_xsd, '', '.', noncompliant_xml)
        self.assertEqual(max_occurs_found, 1)


class ParserManageOccurencesTestSuite(TestCase):
    """
    """

    def setUp(self):
        occurs_data = join('curate', 'tests', 'data', 'parser', 'utils', 'manage_occurs')
        self.occurs_data_handler = DataHandler(occurs_data)

    def test_element_with_min_occurs_parsable(self):
        xsd_element = self.occurs_data_handler.get_xsd2('min_occurs_parsable')
        (min_occ, max_occ) = manage_occurences(xsd_element)

        self.assertEqual(min_occ, 1)

    def test_element_with_max_occurs_unbounded(self):
        xsd_element = self.occurs_data_handler.get_xsd2('max_occurs_unbounded')
        (min_occ, max_occ) = manage_occurences(xsd_element)

        self.assertEqual(max_occ, float('inf'))

    def test_element_with_max_occurs_parsable(self):
        xsd_element = self.occurs_data_handler.get_xsd2('max_occurs_parsable')
        (min_occ, max_occ) = manage_occurences(xsd_element)

        self.assertEqual(max_occ, 5)


class ParserManageAttrOccurencesTestSuite(TestCase):
    """
    """

    def setUp(self):
        occurs_data = join('curate', 'tests', 'data', 'parser', 'utils', 'manage_occurs')
        self.occurs_data_handler = DataHandler(occurs_data)

    def test_use_optional(self):
        xsd_element = self.occurs_data_handler.get_xsd2('attr_use_optional')
        (min_occ, max_occ) = manage_attr_occurrences(xsd_element)

        self.assertEqual(min_occ, 0)
        self.assertEqual(max_occ, 1)

    def test_use_prohibited(self):
        xsd_element = self.occurs_data_handler.get_xsd2('attr_use_prohibited')
        (min_occ, max_occ) = manage_attr_occurrences(xsd_element)

        self.assertEqual(min_occ, 0)
        self.assertEqual(max_occ, 0)

    def test_use_required(self):
        xsd_element = self.occurs_data_handler.get_xsd2('attr_use_required')
        (min_occ, max_occ) = manage_attr_occurrences(xsd_element)

        self.assertEqual(min_occ, 1)
        self.assertEqual(max_occ, 1)

    def test_use_not_present(self):
        xsd_element = self.occurs_data_handler.get_xsd2('attr_use_undefined')
        (min_occ, max_occ) = manage_attr_occurrences(xsd_element)

        # FIXME test broken with current parser
        # self.assertEqual(min_occ, 0)
        self.assertEqual(max_occ, 1)


class ParserHasModuleTestSuite(TestCase):
    """
    """

    def _save_module_to_db(self):
        # FIXME module is not saved in the right database
        module = Module()
        module.name = 'registered_module'
        module.url = 'registered_module'
        module.view = 'registered_module'

        module.save()

    def setUp(self):
        # connect to test database
        # self.db_name = "mgi_test"
        # disconnect()
        # connect(self.db_name, port=27018)

        module_data = join('curate', 'tests', 'data', 'parser', 'utils', 'modules')
        self.module_data_handler = DataHandler(module_data)

    def test_element_is_module_registered(self):
        # expect true
        self._save_module_to_db()

        xsd_element = self.module_data_handler.get_xsd2('registered_module')
        result = has_module(None, xsd_element)

        self.assertTrue(result)

    def test_element_is_module_not_registered(self):
        # expect false
        xsd_element = self.module_data_handler.get_xsd2('unregistered_module')
        result = has_module(None, xsd_element)

        self.assertFalse(result)

    def test_element_is_not_module(self):
        # expect false
        xsd_element = self.module_data_handler.get_xsd2('no_module')
        result = has_module(None, xsd_element)

        self.assertFalse(result)


class ParserGetXmlElementDataTestSuite(TestCase):
    """
    """

    def setUp(self):
        xml_element_data = join('curate', 'tests', 'data', 'parser', 'utils', 'xml_data')
        self.xml_element_data_handler = DataHandler(xml_element_data)

    def test_element_xml_text(self):
        xsd_element = self.xml_element_data_handler.get_xsd2(join('element', 'simple'))
        xml_element = self.xml_element_data_handler.get_xml(join('element', 'simple'))

        reload_data = get_xml_element_data(xsd_element, xml_element, '')
        self.assertEqual(reload_data, 'test')

    def test_element_xml_branch(self):
        xsd_element = self.xml_element_data_handler.get_xsd2(join('element', 'complex'))
        xml_element = self.xml_element_data_handler.get_xml(join('element', 'complex'))

        reload_data = get_xml_element_data(xsd_element, xml_element, '')
        self.assertEqual(reload_data, etree.tostring(xml_element))

    def test_attribute(self):
        xsd_element = self.xml_element_data_handler.get_xsd2(join('attribute', 'schema'))

        reload_data = get_xml_element_data(xsd_element, None, '')
        self.assertEqual(reload_data, None)

    def test_complex_type_xml_empty(self):
        xsd_element = self.xml_element_data_handler.get_xsd2(join('complex_type', 'complex'))
        xml_element = self.xml_element_data_handler.get_xml(join('complex_type', 'empty'))

        reload_data = get_xml_element_data(xsd_element, xml_element, '')
        self.assertEqual(reload_data, "")

    def test_complex_type_xml_branch(self):
        xsd_element = self.xml_element_data_handler.get_xsd2(join('complex_type', 'complex'))
        xml_element = self.xml_element_data_handler.get_xml(join('complex_type', 'complex'))

        reload_data = get_xml_element_data(xsd_element, xml_element, '')
        self.assertEqual(reload_data, etree.tostring(xml_element))

    def test_simple_type_xml_text(self):
        xsd_element = self.xml_element_data_handler.get_xsd2(join('simple_type', 'simple'))
        xml_element = self.xml_element_data_handler.get_xml(join('simple_type', 'simple'))

        reload_data = get_xml_element_data(xsd_element, xml_element, '')
        self.assertEqual(reload_data, "child_0")

    def test_simple_type_empty(self):
        xsd_element = self.xml_element_data_handler.get_xsd2(join('simple_type', 'simple'))
        xml_element = self.xml_element_data_handler.get_xml(join('simple_type', 'empty'))

        reload_data = get_xml_element_data(xsd_element, xml_element, '')
        self.assertEqual(reload_data, "")


class ParserGetElementTypeTestSuite(TestCase):
    """
    """

    def setUp(self):
        self.defaultPrefix = 'xsd'
        self.namespace = ''

        xml_element_data = join('curate', 'tests', 'data', 'parser', 'element_type')
        self.xml_element_data_handler = DataHandler(xml_element_data)

    def test_no_type_one_child_no_annot(self):
        xsd_element = self.xml_element_data_handler.get_xsd2(join('no_type', 'one_child_no_annot'))

        element_type = get_element_type(xsd_element, None, '', 'xsd')
        self.assertEqual(element_type, list(xsd_element)[0])

    def test_no_type_one_child_annot(self):
        xsd_element = self.xml_element_data_handler.get_xsd2(join('no_type', 'one_child_annot'))

        element_type = get_element_type(xsd_element, None, '', 'xsd')
        self.assertEqual(element_type, None)

    def test_no_type_two_children_annot(self):
        xsd_element = self.xml_element_data_handler.get_xsd2(join('no_type', 'two_children_annot'))

        element_type = get_element_type(xsd_element, None, '', 'xsd')
        self.assertEqual(element_type, list(xsd_element)[1])

    def test_no_type_more_children(self):
        xsd_element = self.xml_element_data_handler.get_xsd2(join('no_type', 'more_children'))

        element_type = get_element_type(xsd_element, None, '', 'xsd')
        self.assertEqual(element_type, None)

    def test_type_is_common_type(self):
        xsd_element = self.xml_element_data_handler.get_xsd2('common_type')

        element_type = get_element_type(xsd_element, None, '', 'xsd')
        self.assertEqual(element_type, None)

    # todo make more tests
    def test_type_is_complex_type(self):
        xsd_element = self.xml_element_data_handler.get_xsd2(join('complex_type', 'element'))
        xsd_schema = self.xml_element_data_handler.get_xsd2(join('complex_type', 'schema'))

        result_element = self.xml_element_data_handler.get_xsd2(join('complex_type', 'result'))

        element_type = get_element_type(xsd_element, xsd_schema, '', 'xsd')
        self.assertTrue(are_equals(element_type, result_element))

    def test_type_is_simple_type(self):
        xsd_element = self.xml_element_data_handler.get_xsd2(join('simple_type', 'element'))
        xsd_schema = self.xml_element_data_handler.get_xsd2(join('simple_type', 'schema'))

        result_element = self.xml_element_data_handler.get_xsd2(join('simple_type', 'result'))

        element_type = get_element_type(xsd_element, xsd_schema, '', 'xsd')
        self.assertTrue(are_equals(element_type, result_element))


class ParserRemoveAnnotationTestSuite(TestCase):
    """
    """

    def setUp(self):
        annotation_data = join('curate', 'tests', 'data', 'parser', 'utils', 'annotation')
        self.annotation_data_handler = DataHandler(annotation_data)

        self.namespace = ''

        self.result = self.annotation_data_handler.get_xsd2('not_annot')

    def test_annotation_is_removed(self):
        annotated_schema = self.annotation_data_handler.get_xsd2('annot')
        remove_annotations(annotated_schema, self.namespace)

        self.assertTrue(are_equals(annotated_schema, self.result))

    def test_no_annotation_no_change(self):
        not_annotated_schema = self.annotation_data_handler.get_xsd2('not_annot')
        remove_annotations(not_annotated_schema, self.namespace)

        self.assertTrue(are_equals(not_annotated_schema, self.result))


##################################################
# Part II: Schema parsing testing
##################################################

class ParserGenerateFormTestSuite(TestCase):
    """
    """

    def setUp(self):
        schema_data = join('curate', 'tests', 'data', 'parser', 'schema')
        self.schema_data_handler = DataHandler(schema_data)

        self.request = HttpRequest()
        engine = import_module('django.contrib.sessions.backends.db')
        session_key = None
        self.request.session = engine.SessionStore(session_key)

        self.request.session['curate_edit'] = False  # Data edition

        form_data = FormData()
        form_data.name = ''
        form_data.user = ''
        form_data.template = ''

        form_data.save()

        self.request.session['curateFormData'] = form_data.pk
        self.request.session['nb_html_tags'] = 0
        self.request.session['mapTagID'] = {}
        self.request.session['nbChoicesID'] = 0
        self.request.session['defaultPrefix'] = 'test'
        self.request.session['namespaces'] = {'test': ''}

    def test_create_include(self):
        xsd_files = join('include', 'basic')
        xsd_tree = self.schema_data_handler.get_xsd2(xsd_files)

        self.request.session['xmlDocTree'] = etree.tostring(xsd_tree)

        result_string = generate_form(self.request)

        result_html = etree.fromstring(result_string)
        expected_html = self.schema_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    def test_create_import(self):
        xsd_files = join('import', 'basic')
        xsd_tree = self.schema_data_handler.get_xsd2(xsd_files)

        self.request.session['xmlDocTree'] = etree.tostring(xsd_tree)

        result_string = generate_form(self.request)

        result_html = etree.fromstring(result_string)
        expected_html = self.schema_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    def test_create_redefine(self):
        xsd_files = join('redefine', 'basic')
        xsd_tree = self.schema_data_handler.get_xsd2(xsd_files)

        self.request.session['xmlDocTree'] = etree.tostring(xsd_tree)

        result_string = generate_form(self.request)
        # print result_string
        # self.assertEqual(result_string, '')

        result_html = etree.fromstring(result_string)
        expected_html = self.schema_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    def test_create_simple_type(self):
        xsd_files = join('simple_type', 'basic')
        xsd_tree = self.schema_data_handler.get_xsd2(xsd_files)

        self.request.session['xmlDocTree'] = etree.tostring(xsd_tree)

        result_string = generate_form(self.request)
        # print result_string
        # self.assertEqual(result_string, '')

        result_html = etree.fromstring(result_string)
        expected_html = self.schema_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    def test_create_complex_type(self):
        xsd_files = join('complex_type', 'basic')
        xsd_tree = self.schema_data_handler.get_xsd2(xsd_files)

        self.request.session['xmlDocTree'] = etree.tostring(xsd_tree)

        result_string = generate_form(self.request)
        # print result_string
        # self.assertEqual(result_string, '')

        result_html = etree.fromstring(result_string)
        expected_html = self.schema_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    def test_create_group(self):
        xsd_files = join('group', 'basic')
        xsd_tree = self.schema_data_handler.get_xsd2(xsd_files)

        self.request.session['xmlDocTree'] = etree.tostring(xsd_tree)

        result_string = generate_form(self.request)
        # print result_string
        # self.assertEqual(result_string, '')

        result_html = etree.fromstring(result_string)
        expected_html = self.schema_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    def test_create_attribute_group(self):
        xsd_files = join('attribute_group', 'basic')
        xsd_tree = self.schema_data_handler.get_xsd2(xsd_files)

        self.request.session['xmlDocTree'] = etree.tostring(xsd_tree)

        result_string = generate_form(self.request)
        # print result_string
        # self.assertEqual(result_string, '')

        result_html = etree.fromstring(result_string)
        expected_html = self.schema_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    def test_create_element_basic(self):
        xsd_files = join('element', 'basic')
        xsd_tree = self.schema_data_handler.get_xsd2(xsd_files)

        self.request.session['xmlDocTree'] = etree.tostring(xsd_tree)

        result_string = generate_form(self.request)
        # print result_string
        # self.assertEqual(result_string, '')

        result_html = etree.fromstring(result_string)
        expected_html = self.schema_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    def test_create_element_multiple(self):
        xsd_files = join('element', 'multiple')
        xsd_tree = self.schema_data_handler.get_xsd2(xsd_files)

        self.request.session['xmlDocTree'] = etree.tostring(xsd_tree)

        result_string = generate_form(self.request)
        # print result_string
        # self.assertEqual(result_string, '')

        result_html = etree.fromstring(result_string)
        expected_html = self.schema_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    def test_create_attribute(self):
        xsd_files = join('attribute', 'basic')
        xsd_tree = self.schema_data_handler.get_xsd2(xsd_files)

        self.request.session['xmlDocTree'] = etree.tostring(xsd_tree)

        result_string = generate_form(self.request)
        # print result_string
        # self.assertEqual(result_string, '')

        result_html = etree.fromstring(result_string)
        expected_html = self.schema_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    def test_create_notation(self):
        xsd_files = join('notation', 'basic')
        xsd_tree = self.schema_data_handler.get_xsd2(xsd_files)

        self.request.session['xmlDocTree'] = etree.tostring(xsd_tree)

        result_string = generate_form(self.request)
        # print result_string
        # self.assertEqual(result_string, '')

        result_html = etree.fromstring(result_string)
        expected_html = self.schema_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    def test_create_multiple(self):
        xsd_files = join('multiple', 'basic')
        xsd_tree = self.schema_data_handler.get_xsd2(xsd_files)

        self.request.session['xmlDocTree'] = etree.tostring(xsd_tree)

        result_string = generate_form(self.request)
        # print result_string
        # self.assertEqual(result_string, '')

        result_html = etree.fromstring(result_string)
        expected_html = self.schema_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    # def test_reload_include(self):
    #     xsd_files = join('include', 'basic')
    #     xsd_tree = self.schema_data_handler.get_xsd2(xsd_files)
    #
    #     self.request.session['xmlDocTree'] = etree.tostring(xsd_tree)
    #     self.request.session['curate_edit'] = True
    #
    #     form_data = FormData()
    #
    #     xml_data = self.schema_data_handler.get_xml(xsd_files)
    #
    #     form_data.xml_data = etree.tostring(xml_data)
    #     form_data.name = ''
    #     form_data.user = ''
    #     form_data.template = ''
    #
    #     form_data.save()
    #
    #     self.request.session['curateFormData'] = form_data.pk
    #
    #     result_string = generate_form(self.request)
    #
    #     print result_string
    #     # result_string = '<div>' + result_string + '</div>'
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.schema_data_handler.get_html2(xsd_files + '.reload')
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_reload_import(self):
    #     pass
    #
    # def test_reload_redefine(self):
    #     pass
    #
    # def test_reload_simple_type(self):
    #     pass
    #
    # def test_reload_complex_type(self):
    #     pass
    #
    # def test_reload_group(self):
    #     pass
    #
    # def test_reload_attribute_group(self):
    #     pass

    def test_reload_element(self):
        xsd_files = join('element', 'basic')
        xsd_reload_files = join('element', 'basic.reload')
        xsd_tree = self.schema_data_handler.get_xsd2(xsd_files)

        self.request.session['xmlDocTree'] = etree.tostring(xsd_tree)
        self.request.session['curate_edit'] = True

        form_data = FormData()

        xml_data = self.schema_data_handler.get_xml(xsd_files)

        form_data.xml_data = etree.tostring(xml_data)
        form_data.name = ''
        form_data.user = ''
        form_data.template = ''

        form_data.save()

        self.request.session['curateFormData'] = form_data.pk

        result_string = generate_form(self.request)
        # print result_string
        # self.assertEqual(result_string, '')

        result_html = etree.fromstring(result_string)
        expected_html = self.schema_data_handler.get_html2(xsd_reload_files)

        self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_elements(self):
        xsd_files = join('element', 'multiple')
        xsd_tree = self.schema_data_handler.get_xsd2(xsd_files)

        self.request.session['xmlDocTree'] = etree.tostring(xsd_tree)
        self.request.session['curate_edit'] = True

        form_data = FormData()

        xml_data = self.schema_data_handler.get_xml(xsd_files)

        form_data.xml_data = etree.tostring(xml_data)
        form_data.name = ''
        form_data.user = ''
        form_data.template = ''

        form_data.save()

        self.request.session['curateFormData'] = form_data.pk

        result_string = generate_form(self.request)
        # print result_string
        # self.assertEqual(result_string, '')

        result_html = etree.fromstring(result_string)
        expected_html = self.schema_data_handler.get_html2(xsd_files + '.reload')

        self.assertTrue(are_equals(result_html, expected_html))

    # def test_reload_attribute(self):
    #     pass
    #
    # def test_reload_multiple(self):
    #     pass


class ParserGenerateElementTestSuite(TestCase):
    """
    """

    def setUp(self):
        element_data = join('curate', 'tests', 'data', 'parser', 'element')
        self.element_data_handler = DataHandler(element_data)

        self.request = HttpRequest()
        engine = import_module('django.contrib.sessions.backends.db')
        session_key = None
        self.request.session = engine.SessionStore(session_key)

        self.maxDiff = None

        self.request.session['curate_edit'] = False  # Data edition
        self.request.session['nb_html_tags'] = 0
        self.request.session['mapTagID'] = {}
        self.request.session['nbChoicesID'] = 0
        self.request.session['defaultPrefix'] = 'test'

    def test_create_simple_type_basic(self):
        xsd_files = join('simple_type', 'basic')
        xsd_tree = self.element_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/element')[0]

        result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')

        expected_element = {'value': None, 'tag': 'element', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'simple_type', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'restriction', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': 'child0', 'tag': 'enumeration', 'occurs': (1, 1, 1), 'module': None, 'children': []}, {'value': 'child1', 'tag': 'enumeration', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}]}]}

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.element_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    def test_create_simple_type_unbounded(self):
        xsd_files = join('simple_type', 'unbounded')
        xsd_tree = self.element_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/complexType/sequence/element')[0]

        result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')

        expected_element = {
            'value': None,
            'tag': 'element',
            'occurs': (2.0, 2.0, float('infinity')), 'module': None, 'children': [{'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'simple_type', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'restriction', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': 'child0', 'tag': 'enumeration', 'occurs': (1, 1, 1), 'module': None, 'children': []}, {'value': 'child1', 'tag': 'enumeration', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}]}, {'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'simple_type', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'restriction', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': 'child0', 'tag': 'enumeration', 'occurs': (1, 1, 1), 'module': None, 'children': []}, {'value': 'child1', 'tag': 'enumeration', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}]}]}

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.element_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    def test_create_complex_type_basic(self):
        xsd_files = join('complex_type', 'basic')
        xsd_tree = self.element_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/element')[0]

        result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')

        expected_element = {
            'tag': 'element',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'elem-iter',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'complex_type',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'sequence',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': [
                                        {
                                            'tag': 'element',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': None,
                                            'children': [
                                                {
                                                    'tag': 'elem-iter',
                                                    'occurs': (1, 1, 1),
                                                    'module': None,
                                                    'value': None,
                                                    'children': [
                                                        {
                                                            'tag': 'input',
                                                            'occurs': (1, 1, 1),
                                                            'module': None,
                                                            'value': '',
                                                            'children': []
                                                        }
                                                    ]
                                                }
                                            ]
                                        },
                                        {
                                            'tag': 'element',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': None,
                                            'children': [
                                                {
                                                    'tag': 'elem-iter',
                                                    'occurs': (1, 1, 1),
                                                    'module': None,
                                                    'value': None,
                                                    'children': [
                                                        {
                                                            'tag': 'input',
                                                            'occurs': (1, 1, 1),
                                                            'module': None,
                                                            'value': '',
                                                            'children': []
                                                        }
                                                    ]
                                                }
                                            ]
                                        },
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.element_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    def test_create_complex_type_unbounded(self):
        xsd_files = join('complex_type', 'unbounded')
        xsd_tree = self.element_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/complexType/sequence/element')[0]

        result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')

        expected_element = {
            'tag': 'element',
            'occurs': (2., 2., float('infinity')),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'elem-iter',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'complex_type',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'sequence',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': [
                                        {
                                            'tag': 'element',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': None,
                                            'children': [
                                                {
                                                    'tag': 'elem-iter',
                                                    'occurs': (1, 1, 1),
                                                    'module': None,
                                                    'value': None,
                                                    'children': [
                                                        {
                                                            'tag': 'input',
                                                            'occurs': (1, 1, 1),
                                                            'module': None,
                                                            'value': '',
                                                            'children': []
                                                        }
                                                    ]
                                                }
                                            ]
                                        },
                                        {
                                            'tag': 'element',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': None,
                                            'children': [
                                                {
                                                    'tag': 'elem-iter',
                                                    'occurs': (1, 1, 1),
                                                    'module': None,
                                                    'value': None,
                                                    'children': [
                                                        {
                                                            'tag': 'input',
                                                            'occurs': (1, 1, 1),
                                                            'module': None,
                                                            'value': '',
                                                            'children': []
                                                        }
                                                    ]
                                                }
                                            ]
                                        },
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    'tag': 'elem-iter',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'complex_type',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'sequence',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': [
                                        {
                                            'tag': 'element',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': None,
                                            'children': [
                                                {
                                                    'tag': 'elem-iter',
                                                    'occurs': (1, 1, 1),
                                                    'module': None,
                                                    'value': None,
                                                    'children': [
                                                        {
                                                            'tag': 'input',
                                                            'occurs': (1, 1, 1),
                                                            'module': None,
                                                            'value': '',
                                                            'children': []
                                                        }
                                                    ]
                                                }
                                            ]
                                        },
                                        {
                                            'tag': 'element',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': None,
                                            'children': [
                                                {
                                                    'tag': 'elem-iter',
                                                    'occurs': (1, 1, 1),
                                                    'module': None,
                                                    'value': None,
                                                    'children': [
                                                        {
                                                            'tag': 'input',
                                                            'occurs': (1, 1, 1),
                                                            'module': None,
                                                            'value': '',
                                                            'children': []
                                                        }
                                                    ]
                                                }
                                            ]
                                        },
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.element_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    # def test_create_unique_basic(self):
    #     # TODO implement when support for unique is wanted
    #     xsd_files = join('unique', 'basic')
    #     xsd_tree = self.element_data_handler.get_xsd2(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/element')[0]
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.element_data_handler.get_html2(xsd_files)
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_unique_unbounded(self):
    #     # TODO implement when support for unique is wanted
    #     xsd_files = join('unique', 'unbounded')
    #     xsd_tree = self.element_data_handler.get_xsd2(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence/element')[0]
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.element_data_handler.get_html2(xsd_files)
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_key_basic(self):
    #     # TODO implement when support for key is wanted
    #     xsd_files = join('key', 'basic')
    #     xsd_tree = self.element_data_handler.get_xsd2(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/element')[0]
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.element_data_handler.get_html2(xsd_files)
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_key_unbounded(self):
    #     # TODO implement when support for key is wanted
    #     xsd_files = join('key', 'unbounded')
    #     xsd_tree = self.element_data_handler.get_xsd2(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence/element')[0]
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.element_data_handler.get_html2(xsd_files)
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_keyref_basic(self):
    #     # TODO implement when support for keyref is wanted
    #     xsd_files = join('keyref', 'basic')
    #     xsd_tree = self.element_data_handler.get_xsd2(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/element')[0]
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.element_data_handler.get_html2(xsd_files)
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_keyref_unbounded(self):
    #     # TODO implement when support for keyref is wanted
    #     xsd_files = join('keyref', 'unbounded')
    #     xsd_tree = self.element_data_handler.get_xsd2(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence/element')[0]
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.element_data_handler.get_html2(xsd_files)
    #
    #     self.assertTrue(are_equals(result_html, expected_html))

    # TODO Implement unique, key and keyref for these tests
    # def test_create_simple_unique_basic(self):
    #     xsd_tree = self.sequence_data_handler.get_xsd2(join('element', 'basic'))
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.sequence_data_handler.get_html2(join('element', 'basic'))
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_simple_unique_unbounded(self):
    #     xsd_tree = self.sequence_data_handler.get_xsd2(join('element', 'basic'))
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.sequence_data_handler.get_html2(join('element', 'basic'))
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_simple_key_basic(self):
    #     xsd_tree = self.sequence_data_handler.get_xsd2(join('element', 'basic'))
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.sequence_data_handler.get_html2(join('element', 'basic'))
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_simple_key_unbounded(self):
    #     xsd_tree = self.sequence_data_handler.get_xsd2(join('element', 'basic'))
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.sequence_data_handler.get_html2(join('element', 'basic'))
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_simple_keyref_basic(self):
    #     xsd_tree = self.sequence_data_handler.get_xsd2(join('element', 'basic'))
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.sequence_data_handler.get_html2(join('element', 'basic'))
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_simple_keyref_unbounded(self):
    #     xsd_tree = self.sequence_data_handler.get_xsd2(join('element', 'basic'))
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.sequence_data_handler.get_html2(join('element', 'basic'))
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_complex_unique_basic(self):
    #     xsd_tree = self.sequence_data_handler.get_xsd2(join('element', 'basic'))
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.sequence_data_handler.get_html2(join('element', 'basic'))
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_complex_unique_unbounded(self):
    #     xsd_tree = self.sequence_data_handler.get_xsd2(join('element', 'basic'))
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.sequence_data_handler.get_html2(join('element', 'basic'))
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_complex_key_basic(self):
    #     xsd_tree = self.sequence_data_handler.get_xsd2(join('element', 'basic'))
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.sequence_data_handler.get_html2(join('element', 'basic'))
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_complex_key_unbounded(self):
    #     xsd_tree = self.sequence_data_handler.get_xsd2(join('element', 'basic'))
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.sequence_data_handler.get_html2(join('element', 'basic'))
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_complex_keyref_basic(self):
    #     xsd_tree = self.sequence_data_handler.get_xsd2(join('element', 'basic'))
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.sequence_data_handler.get_html2(join('element', 'basic'))
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_complex_keyref_unbounded(self):
    #     xsd_tree = self.sequence_data_handler.get_xsd2(join('element', 'basic'))
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.sequence_data_handler.get_html2(join('element', 'basic'))
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_multiple_basic(self):
    #     xsd_tree = self.sequence_data_handler.get_xsd2(join('element', 'basic'))
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.sequence_data_handler.get_html2(join('element', 'basic'))
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_multiple_unbounded(self):
    #     xsd_tree = self.sequence_data_handler.get_xsd2(join('element', 'basic'))
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.sequence_data_handler.get_html2(join('element', 'basic'))
    #
    #     self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_simple_type_basic(self):
        xsd_files = join('simple_type', 'basic')
        xsd_tree = self.element_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/element')[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.element_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))

        result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='',
                                         edit_data_tree=edit_data_tree)

        expected_element = {'value': None, 'tag': 'element', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'simple_type', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'restriction', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': 'child0', 'tag': 'enumeration/selected', 'occurs': (1, 1, 1), 'module': None, 'children': []}, {'value': 'child1', 'tag': 'enumeration', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}]}]}

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.element_data_handler.get_html2(xsd_files + '.reload')

        self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_simple_type_unbounded(self):
        xsd_files = join('simple_type', 'unbounded')
        xsd_tree = self.element_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/complexType/sequence/element')[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.element_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))

        result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='/root',
                                         edit_data_tree=edit_data_tree)

        expected_element = {'value': None, 'tag': 'element', 'occurs': (2.0, 3, float('infinity')), 'module': None, 'children': [{'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'simple_type', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'restriction', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': 'child0', 'tag': 'enumeration', 'occurs': (1, 1, 1), 'module': None, 'children': []}, {'value': 'child1', 'tag': 'enumeration/selected', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}]}, {'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'simple_type', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'restriction', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': 'child0', 'tag': 'enumeration', 'occurs': (1, 1, 1), 'module': None, 'children': []}, {'value': 'child1', 'tag': 'enumeration/selected', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}]}, {'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'simple_type', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'restriction', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': 'child0', 'tag': 'enumeration/selected', 'occurs': (1, 1, 1), 'module': None, 'children': []}, {'value': 'child1', 'tag': 'enumeration', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}]}]}

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.element_data_handler.get_html2(xsd_files + '.reload')

        self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_complex_type_basic(self):
        xsd_files = join('complex_type', 'basic')
        xsd_tree = self.element_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/element')[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.element_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))

        result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='',
                                         edit_data_tree=edit_data_tree)

        expected_element = {
            'tag': 'element',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'elem-iter',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'complex_type',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'sequence',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': [
                                        {
                                            'tag': 'element',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': None,
                                            'children': [
                                                {
                                                    'tag': 'elem-iter',
                                                    'occurs': (1, 1, 1),
                                                    'module': None,
                                                    'value': None,
                                                    'children': [
                                                        {
                                                            'tag': 'input',
                                                            'occurs': (1, 1, 1),
                                                            'module': None,
                                                            'value': 'entry0',
                                                            'children': []
                                                        }
                                                    ]
                                                }
                                            ]
                                        },
                                        {
                                            'tag': 'element',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': None,
                                            'children': [
                                                {
                                                    'tag': 'elem-iter',
                                                    'occurs': (1, 1, 1),
                                                    'module': None,
                                                    'value': None,
                                                    'children': [
                                                        {
                                                            'tag': 'input',
                                                            'occurs': (1, 1, 1),
                                                            'module': None,
                                                            'value': 'entry1',
                                                            'children': []
                                                        }
                                                    ]
                                                }
                                            ]
                                        },
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.element_data_handler.get_html2(xsd_files + '.reload')

        self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_complex_type_unbounded(self):
        xsd_files = join('complex_type', 'unbounded')
        xsd_tree = self.element_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/complexType/sequence/element')[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.element_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))

        result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='/root',
                                         edit_data_tree=edit_data_tree)

        expected_element = {
            'tag': 'element',
            'occurs': (2., 3, float('infinity')),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'elem-iter',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'complex_type',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'sequence',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': [
                                        {
                                            'tag': 'element',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': None,
                                            'children': [
                                                {
                                                    'tag': 'elem-iter',
                                                    'occurs': (1, 1, 1),
                                                    'module': None,
                                                    'value': None,
                                                    'children': [
                                                        {
                                                            'tag': 'input',
                                                            'occurs': (1, 1, 1),
                                                            'module': None,
                                                            'value': 'entry0',
                                                            'children': []
                                                        }
                                                    ]
                                                }
                                            ]
                                        },
                                        {
                                            'tag': 'element',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': None,
                                            'children': [
                                                {
                                                    'tag': 'elem-iter',
                                                    'occurs': (1, 1, 1),
                                                    'module': None,
                                                    'value': None,
                                                    'children': [
                                                        {
                                                            'tag': 'input',
                                                            'occurs': (1, 1, 1),
                                                            'module': None,
                                                            'value': 'entry1',
                                                            'children': []
                                                        }
                                                    ]
                                                }
                                            ]
                                        },
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    'tag': 'elem-iter',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'complex_type',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'sequence',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': [
                                        {
                                            'tag': 'element',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': None,
                                            'children': [
                                                {
                                                    'tag': 'elem-iter',
                                                    'occurs': (1, 1, 1),
                                                    'module': None,
                                                    'value': None,
                                                    'children': [
                                                        {
                                                            'tag': 'input',
                                                            'occurs': (1, 1, 1),
                                                            'module': None,
                                                            'value': 'entry2',
                                                            'children': []
                                                        }
                                                    ]
                                                }
                                            ]
                                        },
                                        {
                                            'tag': 'element',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': None,
                                            'children': [
                                                {
                                                    'tag': 'elem-iter',
                                                    'occurs': (1, 1, 1),
                                                    'module': None,
                                                    'value': None,
                                                    'children': [
                                                        {
                                                            'tag': 'input',
                                                            'occurs': (1, 1, 1),
                                                            'module': None,
                                                            'value': 'entry3',
                                                            'children': []
                                                        }
                                                    ]
                                                }
                                            ]
                                        },
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    'tag': 'elem-iter',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'complex_type',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'sequence',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': [
                                        {
                                            'tag': 'element',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': None,
                                            'children': [
                                                {
                                                    'tag': 'elem-iter',
                                                    'occurs': (1, 1, 1),
                                                    'module': None,
                                                    'value': None,
                                                    'children': [
                                                        {
                                                            'tag': 'input',
                                                            'occurs': (1, 1, 1),
                                                            'module': None,
                                                            'value': 'entry4',
                                                            'children': []
                                                        }
                                                    ]
                                                }
                                            ]
                                        },
                                        {
                                            'tag': 'element',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': None,
                                            'children': [
                                                {
                                                    'tag': 'elem-iter',
                                                    'occurs': (1, 1, 1),
                                                    'module': None,
                                                    'value': None,
                                                    'children': [
                                                        {
                                                            'tag': 'input',
                                                            'occurs': (1, 1, 1),
                                                            'module': None,
                                                            'value': 'entry5',
                                                            'children': []
                                                        }
                                                    ]
                                                }
                                            ]
                                        },
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        self.maxDiff = None
        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.element_data_handler.get_html2(xsd_files + '.reload')

        self.assertTrue(are_equals(result_html, expected_html))

    # todo implement these test when the parser implement the functionalities
    # def test_reload_unique_basic(self):
    #     xsd_files = join('unique', 'basic')
    #     xsd_tree = self.element_data_handler.get_xsd2(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/element')[0]
    #
    #     self.request.session['curate_edit'] = True
    #
    #     xml_tree = self.element_data_handler.get_xml(xsd_files)
    #     xml_data = etree.tostring(xml_tree)
    #
    #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
    #     etree.set_default_parser(parser=clean_parser)
    #     # load the XML tree from the text
    #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='',
    #                                     edit_data_tree=edit_data_tree)
    #     print result_string
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.element_data_handler.get_html2(xsd_files + '.reload')
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))

    # def test_reload_unique_unbounded(self):
    #     xsd_files = join('complex_type', 'unbounded')
    #     xsd_tree = self.element_data_handler.get_xsd2(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence/element')[0]
    #
    #     self.request.session['curate_edit'] = True
    #
    #     xml_tree = self.element_data_handler.get_xml(xsd_files)
    #     xml_data = etree.tostring(xml_tree)
    #
    #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
    #     etree.set_default_parser(parser=clean_parser)
    #     # load the XML tree from the text
    #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='/root',
    #                                     edit_data_tree=edit_data_tree)
    #     print result_string
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.element_data_handler.get_html2(xsd_files + '.reload')
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_reload_key_basic(self):
    #     xsd_files = join('simple_type', 'basic')
    #     xsd_tree = self.element_data_handler.get_xsd2(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/element')[0]
    #
    #     self.request.session['curate_edit'] = True
    #
    #     xml_tree = self.element_data_handler.get_xml(xsd_files)
    #     xml_data = etree.tostring(xml_tree)
    #
    #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
    #     etree.set_default_parser(parser=clean_parser)
    #     # load the XML tree from the text
    #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='',
    #                                     edit_data_tree=edit_data_tree)
    #     print result_string
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.element_data_handler.get_html2(xsd_files + '.reload')
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_reload_key_unbounded(self):
    #     xsd_files = join('complex_type', 'unbounded')
    #     xsd_tree = self.element_data_handler.get_xsd2(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence/element')[0]
    #
    #     self.request.session['curate_edit'] = True
    #
    #     xml_tree = self.element_data_handler.get_xml(xsd_files)
    #     xml_data = etree.tostring(xml_tree)
    #
    #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
    #     etree.set_default_parser(parser=clean_parser)
    #     # load the XML tree from the text
    #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='/root',
    #                                     edit_data_tree=edit_data_tree)
    #     print result_string
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.element_data_handler.get_html2(xsd_files + '.reload')
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_reload_keyref_basic(self):
    #     xsd_files = join('simple_type', 'basic')
    #     xsd_tree = self.element_data_handler.get_xsd2(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/element')[0]
    #
    #     self.request.session['curate_edit'] = True
    #
    #     xml_tree = self.element_data_handler.get_xml(xsd_files)
    #     xml_data = etree.tostring(xml_tree)
    #
    #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
    #     etree.set_default_parser(parser=clean_parser)
    #     # load the XML tree from the text
    #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='',
    #                                     edit_data_tree=edit_data_tree)
    #     print result_string
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.element_data_handler.get_html2(xsd_files + '.reload')
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_reload_keyref_unbounded(self):
    #     xsd_files = join('complex_type', 'unbounded')
    #     xsd_tree = self.element_data_handler.get_xsd2(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence/element')[0]
    #
    #     self.request.session['curate_edit'] = True
    #
    #     xml_tree = self.element_data_handler.get_xml(xsd_files)
    #     xml_data = etree.tostring(xml_tree)
    #
    #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
    #     etree.set_default_parser(parser=clean_parser)
    #     # load the XML tree from the text
    #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
    #
    #     result_string = generate_element(self.request, xsd_element, xsd_tree, '', full_path='/root',
    #                                     edit_data_tree=edit_data_tree)
    #     print result_string
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.element_data_handler.get_html2(xsd_files + '.reload')
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))


class ParserGenerateElementAbsentTestSuite(TestCase):
    """
    """

    def setUp(self):
        element_data = join('curate', 'tests', 'data', 'parser', 'element_absent')
        self.element_data_handler = DataHandler(element_data)

        self.request = HttpRequest()
        engine = import_module('django.contrib.sessions.backends.db')
        session_key = None

        self.maxDiff = None
        self.request.session = engine.SessionStore(session_key)

        self.request.session['curate_edit'] = False  # Data edition
        self.request.session['nb_html_tags'] = 0
        self.request.session['mapTagID'] = {}
        self.request.session['nbChoicesID'] = 0
        self.request.session['defaultPrefix'] = 'test'
        self.request.session['namespaces'] = {'test': ''}

        self.form_element = FormElement()
        self.form_element.xml_xpath = ''

    def test_create_simple_type_basic(self):
        xsd_files = join('simple_type', 'basic')
        xsd_tree = self.element_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/element')[0]

        result_string = generate_element_absent(self.request, xsd_element, xsd_tree, self.form_element)

        expected_element = {'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'simple_type', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'restriction', 'occurs': (1, 1, 1), 'module': None, 'children': [{'module': None, 'tag': 'input', 'occurs': (1, 1, 1), 'value': '', 'children': []}]}]}]}

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.element_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    def test_create_simple_type_unbounded(self):
        xsd_files = join('simple_type', 'unbounded')
        xsd_tree = self.element_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/element')[0]

        result_string = generate_element_absent(self.request, xsd_element, xsd_tree, self.form_element)

        expected_element = {'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'simple_type', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'restriction', 'occurs': (1, 1, 1), 'module': None, 'children': [{'module': None, 'tag': 'input', 'occurs': (1, 1, 1), 'value': '', 'children': []}]}]}]}

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.element_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    def test_create_complex_type_basic(self):
        xsd_files = join('complex_type', 'basic')
        xsd_tree = self.element_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/element')[0]

        result_string = generate_element_absent(self.request, xsd_element, xsd_tree, self.form_element)

        expected_element = {
            'tag': 'elem-iter',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'complex_type',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'sequence',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'element',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': [
                                        {
                                            'tag': 'elem-iter',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': None,
                                            'children': [
                                                {
                                                    'tag': 'input',
                                                    'occurs': (1, 1, 1),
                                                    'module': None,
                                                    'value': '',
                                                    'children': []
                                                },
                                            ]
                                        },
                                    ]
                                },
                                {
                                    'tag': 'element',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': [
                                        {
                                            'tag': 'elem-iter',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': None,
                                            'children': [
                                                {
                                                    'tag': 'input',
                                                    'occurs': (1, 1, 1),
                                                    'module': None,
                                                    'value': '',
                                                    'children': []
                                                },
                                            ]
                                        },
                                    ]
                                },
                            ]
                        }
                    ]
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_element)

        result_string = '<div>' + result_string[0] + '</div>'

        result_html = etree.fromstring(result_string)
        expected_html = self.element_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    def test_create_complex_type_unbounded(self):
        xsd_files = join('complex_type', 'unbounded')
        xsd_tree = self.element_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/element')[0]

        result_string = generate_element_absent(self.request, xsd_element, xsd_tree, self.form_element)

        expected_element = {
            'tag': 'elem-iter',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'complex_type',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'sequence',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'element',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': [
                                        {
                                            'tag': 'elem-iter',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': None,
                                            'children': [
                                                {
                                                    'tag': 'input',
                                                    'occurs': (1, 1, 1),
                                                    'module': None,
                                                    'value': '',
                                                    'children': []
                                                },
                                            ]
                                        },
                                    ]
                                },
                                {
                                    'tag': 'element',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': [
                                        {
                                            'tag': 'elem-iter',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': None,
                                            'children': [
                                                {
                                                    'tag': 'input',
                                                    'occurs': (1, 1, 1),
                                                    'module': None,
                                                    'value': '',
                                                    'children': []
                                                },
                                            ]
                                        },
                                    ]
                                },
                            ]
                        }
                    ]
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_element)

        result_string = '<div>' + result_string[0] + '</div>'

        result_html = etree.fromstring(result_string)
        expected_html = self.element_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    # def test_create_unique_basic(self):
    #     # TODO Verify this test is correct
    #     xsd_files = join('unique', 'basic')
    #     xsd_tree = self.element_data_handler.get_xsd2(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/element')[0]
    #
    #     result_string = generate_element_absent(self.request, xsd_element, xsd_tree, self.form_element)
    #     # print result_string
    #     self.assertEqual(result_string, '')
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.element_data_handler.get_html2(xsd_files)
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_unique_unbounded(self):
    #     xsd_files = join('unique', 'unbounded')
    #     xsd_tree = self.element_data_handler.get_xsd2(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/element')[0]
    #
    #     result_string = generate_element_absent(self.request, xsd_element, xsd_tree, self.form_element)
    #     # print result_string
    #     self.assertEqual(result_string, '')
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.element_data_handler.get_html2(xsd_files)
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_key_basic(self):
    #     # TODO Rewrite the test for key / keyref
    #     xsd_files = join('key', 'basic')
    #     xsd_tree = self.element_data_handler.get_xsd2(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/element')[0]
    #
    #     result_string = generate_element_absent(self.request, xsd_element, xsd_tree, self.form_element)
    #     # print result_string
    #     self.assertEqual(result_string, '')
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.element_data_handler.get_html2(xsd_files)
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_key_unbounded(self):
    #     xsd_files = join('key', 'unbounded')
    #     xsd_tree = self.element_data_handler.get_xsd2(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/element')[0]
    #
    #     result_string = generate_element_absent(self.request, xsd_element, xsd_tree, self.form_element)
    #     # print result_string
    #     self.assertEqual(result_string, '')
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.element_data_handler.get_html2(xsd_files)
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_keyref_basic(self):
    #     # TODO Rewrite the test for key / keyref
    #     xsd_files = join('keyref', 'basic')
    #     xsd_tree = self.element_data_handler.get_xsd2(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/element')[0]
    #
    #     result_string = generate_element_absent(self.request, xsd_element, xsd_tree, self.form_element)
    #     # print result_string
    #     self.assertEqual(result_string, '')
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.element_data_handler.get_html2(xsd_files)
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_keyref_unbounded(self):
    #     xsd_files = join('keyref', 'unbounded')
    #     xsd_tree = self.element_data_handler.get_xsd2(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/element')[0]
    #
    #     result_string = generate_element_absent(self.request, xsd_element, xsd_tree, self.form_element)
    #     # print result_string
    #     self.assertEqual(result_string, '')
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.element_data_handler.get_html2(xsd_files)
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))


class ParserGenerateSequenceTestSuite(TestCase):
    """
    """

    def setUp(self):
        sequence_data = join('curate', 'tests', 'data', 'parser', 'sequence')
        self.sequence_data_handler = DataHandler(sequence_data)

        self.maxDiff = None

        self.request = HttpRequest()
        engine = import_module('django.contrib.sessions.backends.db')
        session_key = None
        self.request.session = engine.SessionStore(session_key)

        self.request.session['curate_edit'] = False  # Data edition
        self.request.session['nb_html_tags'] = 0
        self.request.session['mapTagID'] = {}
        self.request.session['nbChoicesID'] = 0
        self.request.session['defaultPrefix'] = 'test'

    def test_create_element_basic(self):
        xsd_tree = self.sequence_data_handler.get_xsd2(join('element', 'basic'))
        xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]

        result_string = generate_sequence(self.request, xsd_element, xsd_tree, '', full_path='')

        expected_element = {'value': None, 'tag': 'sequence', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'element', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': '', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}]}

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.sequence_data_handler.get_html2(join('element', 'basic'))

        self.assertTrue(are_equals(result_html, expected_html))

    def test_create_element_unbounded(self):
        xsd_tree = self.sequence_data_handler.get_xsd2(join('element', 'unbounded'))
        xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]

        result_string = generate_sequence(self.request, xsd_element, xsd_tree, '', full_path='')

        expected_element = {'value': None, 'tag': 'sequence', 'occurs': (2.0, 2.0, float('infinity')), 'module': None, 'children': [{'value': None, 'tag': 'sequence-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'element', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': '', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}]}, {'value': None, 'tag': 'sequence-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'element', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': '', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}]}]}

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.sequence_data_handler.get_html2(join('element', 'unbounded'))

        self.assertTrue(are_equals(result_html, expected_html))

    # def test_create_group_basic(self):
    #     # FIXME change test and implement group support on the parser
    #     xsd_tree = self.sequence_data_handler.get_xsd2(join('group', 'basic'))
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     result_string = generate_sequence(self.request, xsd_element, xsd_tree, '', full_path='')
    #     self.assertEqual(result_string, "")
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.sequence_data_handler.get_html2(join('element', 'element'))
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_group_unbounded(self):
    #     xsd_tree = self.sequence_data_handler.get_xsd2(join('group', 'unbounded'))
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     result_string = generate_sequence(self.request, xsd_element, xsd_tree, '', full_path='')
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.sequence_data_handler.get_html2(join('group', 'unbounded'))
    #
    #     self.assertTrue(are_equals(result_html, expected_html))

    def test_create_choice_basic(self):
        xsd_tree = self.sequence_data_handler.get_xsd2(join('choice', 'basic'))
        xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]

        result_string = generate_sequence(self.request, xsd_element, xsd_tree, '', full_path='')
        # print result_string

        expected_element = {'value': None, 'tag': 'sequence', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'choice', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'choice-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'element', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': '', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}, {'value': None, 'tag': 'element', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}]}

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.sequence_data_handler.get_html2(join('choice', 'basic'))

        self.assertTrue(are_equals(result_html, expected_html))

    def test_create_choice_unbounded(self):
        xsd_tree = self.sequence_data_handler.get_xsd2(join('choice', 'unbounded'))
        xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]

        result_string = generate_sequence(self.request, xsd_element, xsd_tree, '', full_path='')
        # print result_string

        expected_element = {'value': None, 'tag': 'sequence', 'occurs': (2.0, 2.0, float('infinity')), 'module': None, 'children': [{'value': None, 'tag': 'sequence-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'choice', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'choice-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'element', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': '', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}, {'value': None, 'tag': 'element', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}]}, {'value': None, 'tag': 'sequence-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'choice', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'choice-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'element', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': '', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}, {'value': None, 'tag': 'element', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}]}]}

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.sequence_data_handler.get_html2(join('choice', 'unbounded'))

        self.assertTrue(are_equals(result_html, expected_html))

    def test_create_sequence_basic(self):
        xsd_tree = self.sequence_data_handler.get_xsd2(join('sequence', 'basic'))
        xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]

        result_string = generate_sequence(self.request, xsd_element, xsd_tree, '', full_path='')
        # print result_string

        expected_element = {'value': None, 'tag': 'sequence', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'sequence', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'element', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': '', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}]}]}

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.sequence_data_handler.get_html2(join('sequence', 'basic'))

        self.assertTrue(are_equals(result_html, expected_html))

    def test_create_sequence_unbounded(self):
        xsd_tree = self.sequence_data_handler.get_xsd2(join('sequence', 'unbounded'))
        xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]

        result_string = generate_sequence(self.request, xsd_element, xsd_tree, '', full_path='')
        # print result_string

        expected_element = {'value': None, 'tag': 'sequence', 'occurs': (2.0, 2.0, float('infinity')), 'module': None, 'children': [{'value': None, 'tag': 'sequence-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'sequence', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'element', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': '', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}]}]}, {'value': None, 'tag': 'sequence-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'sequence', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'element', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': '', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}]}]}]}

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.sequence_data_handler.get_html2(join('sequence', 'unbounded'))

        self.assertTrue(are_equals(result_html, expected_html))

    # def test_create_any_basic(self):
    #     # FIXME How do we want to handle any's?
    #     xsd_tree = self.sequence_data_handler.get_xsd2(join('any', 'basic'))
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     result_string = generate_sequence(self.request, xsd_element, xsd_tree, '', full_path='')
    #     self.assertEqual(result_string, '')
    #
    # def test_create_any_unbounded(self):
    #     # FIXME How do we want to handle any's?
    #     xsd_tree = self.sequence_data_handler.get_xsd2(join('any', 'unbounded'))
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     result_string = generate_sequence(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.sequence_data_handler.get_html2(join('any', 'unbounded'))
    #
    #     self.assertTrue(are_equals(result_html, expected_html))

    def test_create_multiple_basic(self):
        xsd_tree = self.sequence_data_handler.get_xsd2(join('multiple', 'basic'))
        xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]

        result_string = generate_sequence(self.request, xsd_element, xsd_tree, '', full_path='')

        expected_element = {'value': None, 'tag': 'sequence', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'choice', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'choice-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'element', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': '', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}, {'value': None, 'tag': 'element', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}, {'value': None, 'tag': 'element', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': '', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}, {'value': None, 'tag': 'sequence', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'element', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': '', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}, {'value': None, 'tag': 'element', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': '', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}]}]}

        self.assertDictEqual(result_string[1], expected_element)

        result_string = '<div>' + result_string[0] + '</div>'

        result_html = etree.fromstring(result_string)
        expected_html = self.sequence_data_handler.get_html2(join('multiple', 'basic'))

        self.assertTrue(are_equals(result_html, expected_html))

    def test_create_multiple_unbounded(self):
        xsd_tree = self.sequence_data_handler.get_xsd2(join('multiple', 'unbounded'))
        xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]

        result_string = generate_sequence(self.request, xsd_element, xsd_tree, '', full_path='')
        # print result_string

        expected_element = {'value': None, 'tag': 'sequence', 'occurs': (2.0, 2.0, float('infinity')), 'module': None, 'children': [{'value': None, 'tag': 'sequence-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'choice', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'choice-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'element', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': '', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}, {'value': None, 'tag': 'element', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}, {'value': None, 'tag': 'element', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': '', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}, {'value': None, 'tag': 'sequence', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'element', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': '', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}, {'value': None, 'tag': 'element', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': '', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}]}]}, {'value': None, 'tag': 'sequence-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'choice', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'choice-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'element', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': '', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}, {'value': None, 'tag': 'element', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}, {'value': None, 'tag': 'element', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': '', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}, {'value': None, 'tag': 'sequence', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'element', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': '', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}, {'value': None, 'tag': 'element', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': '', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}]}]}]}

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.sequence_data_handler.get_html2(join('multiple', 'unbounded'))

        self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_element_basic(self):
        xsd_files = join('element', 'basic')
        xsd_tree = self.sequence_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.sequence_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_sequence(self.request, xsd_element, xsd_tree, '', full_path='/root',
                                          edit_data_tree=edit_data_tree)
        # print result_string

        expected_element = {'value': None, 'tag': 'sequence', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'element', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': 'entry0', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}]}

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.sequence_data_handler.get_html2(xsd_files + '.reload')

        self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_element_unbounded(self):
        # fixme correct bug
        xsd_files = join('element', 'unbounded')
        xsd_tree = self.sequence_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.sequence_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_sequence(self.request, xsd_element, xsd_tree, '', full_path='/root',
                                          edit_data_tree=edit_data_tree)
        # print result_string

        expected_element = {'value': None, 'tag': 'sequence', 'occurs': (2.0, 1, float('infinity')), 'module': None, 'children': [{'value': None, 'tag': 'sequence-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'element', 'occurs': (1, 3, 1), 'module': None, 'children': [{'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': 'entry0', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}, {'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': 'entry1', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}, {'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': 'entry2', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}]}]}

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.sequence_data_handler.get_html2(xsd_files + '.reload')

        self.assertTrue(are_equals(result_html, expected_html))

    # fixme implement groups
    # def test_reload_group_basic(self):
    #     xsd_files = join('element', 'basic')
    #     xsd_tree = self.sequence_data_handler.get_xsd2(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     self.request.session['curate_edit'] = True
    #
    #     xml_tree = self.sequence_data_handler.get_xml(xsd_files)
    #     xml_data = etree.tostring(xml_tree)
    #
    #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
    #     etree.set_default_parser(parser=clean_parser)
    #     # load the XML tree from the text
    #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
    #     result_string = generate_sequence(self.request, xsd_element, xsd_tree, '', full_path='/root',
    #                                    edit_data_tree=edit_data_tree)
    #     print result_string
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.sequence_data_handler.get_html2(xsd_files + '.reload')
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_reload_group_unbounded(self):
    #     xsd_files = join('element', 'basic')
    #     xsd_tree = self.sequence_data_handler.get_xsd2(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     self.request.session['curate_edit'] = True
    #
    #     xml_tree = self.sequence_data_handler.get_xml(xsd_files)
    #     xml_data = etree.tostring(xml_tree)
    #
    #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
    #     etree.set_default_parser(parser=clean_parser)
    #     # load the XML tree from the text
    #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
    #     result_string = generate_sequence(self.request, xsd_element, xsd_tree, '', full_path='/root',
    #                                    edit_data_tree=edit_data_tree)
    #     print result_string
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.sequence_data_handler.get_html2(xsd_files + '.reload')
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_choice_basic(self):
        xsd_files = join('choice', 'basic')
        xsd_tree = self.sequence_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.sequence_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_sequence(self.request, xsd_element, xsd_tree, '', full_path='/root',
                                          edit_data_tree=edit_data_tree)
        # print result_string

        expected_element = {'value': None, 'tag': 'sequence', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'choice', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'choice-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'element', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': 'entry0', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}, {'value': None, 'tag': 'element', 'occurs': (1, 0, 1), 'module': None, 'children': []}]}]}]}

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.sequence_data_handler.get_html2(xsd_files + '.reload')

        self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_choice_unbounded(self):
        xsd_files = join('choice', 'unbounded')
        xsd_tree = self.sequence_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.sequence_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_sequence(self.request, xsd_element, xsd_tree, '', full_path='/root',
                                          edit_data_tree=edit_data_tree)
        # print result_string

        expected_element = {'value': None, 'tag': 'sequence', 'occurs': (2.0, 1, float('infinity')), 'module': None, 'children': [{'value': None, 'tag': 'sequence-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'choice', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'choice-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'element', 'occurs': (1, 2, 1), 'module': None, 'children': [{'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': 'entry1', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}, {'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': 'entry2', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}, {'value': None, 'tag': 'element', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': 'entry0', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}]}]}]}]}

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.sequence_data_handler.get_html2(xsd_files + '.reload')

        self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_sequence_basic(self):
        xsd_files = join('sequence', 'basic')
        xsd_tree = self.sequence_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.sequence_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_sequence(self.request, xsd_element, xsd_tree, '', full_path='/root',
                                          edit_data_tree=edit_data_tree)
        # print result_string

        expected_element = {'value': None, 'tag': 'sequence', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'sequence', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'element', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': 'entry0', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}]}]}

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.sequence_data_handler.get_html2(xsd_files + '.reload')

        self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_sequence_unbounded(self):
        xsd_files = join('sequence', 'unbounded')
        xsd_tree = self.sequence_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.sequence_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_sequence(self.request, xsd_element, xsd_tree, '', full_path='/root',
                                          edit_data_tree=edit_data_tree)
        # print result_string

        expected_element = {'value': None, 'tag': 'sequence', 'occurs': (2.0, 1, float('infinity')), 'module': None, 'children': [{'value': None, 'tag': 'sequence-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'sequence', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'element', 'occurs': (1, 3, 1), 'module': None, 'children': [{'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': 'entry0', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}, {'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': 'entry1', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}, {'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': 'entry2', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}]}]}]}

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.sequence_data_handler.get_html2(xsd_files + '.reload')

        self.assertTrue(are_equals(result_html, expected_html))

    # TODO implement tests
    # def test_reload_any_basic(self):
    #     xsd_files = join('element', 'basic')
    #     xsd_tree = self.sequence_data_handler.get_xsd2(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     self.request.session['curate_edit'] = True
    #
    #     xml_tree = self.sequence_data_handler.get_xml(xsd_files)
    #     xml_data = etree.tostring(xml_tree)
    #
    #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
    #     etree.set_default_parser(parser=clean_parser)
    #     # load the XML tree from the text
    #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
    #     result_string = generate_sequence(self.request, xsd_element, xsd_tree, '', full_path='/root',
    #                                    edit_data_tree=edit_data_tree)
    #     print result_string
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.sequence_data_handler.get_html2(xsd_files + '.reload')
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_reload_any_unbounded(self):
    #     xsd_files = join('element', 'basic')
    #     xsd_tree = self.sequence_data_handler.get_xsd2(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     self.request.session['curate_edit'] = True
    #
    #     xml_tree = self.sequence_data_handler.get_xml(xsd_files)
    #     xml_data = etree.tostring(xml_tree)
    #
    #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
    #     etree.set_default_parser(parser=clean_parser)
    #     # load the XML tree from the text
    #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
    #     result_string = generate_sequence(self.request, xsd_element, xsd_tree, '', full_path='/root',
    #                                    edit_data_tree=edit_data_tree)
    #     print result_string
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.sequence_data_handler.get_html2(xsd_files + '.reload')
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_multiple_basic(self):
        xsd_files = join('multiple', 'basic')
        xsd_tree = self.sequence_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.sequence_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_sequence(self.request, xsd_element, xsd_tree, '', full_path='/root',
                                          edit_data_tree=edit_data_tree)


        expected_element = {'value': None, 'tag': 'sequence', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'choice', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'choice-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'element', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': 'entry0', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}, {'value': None, 'tag': 'element', 'occurs': (1, 0, 1), 'module': None, 'children': []}]}]}, {'value': None, 'tag': 'element', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': 'entry1', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}, {'value': None, 'tag': 'sequence', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'element', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': 'entry2', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}, {'value': None, 'tag': 'element', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': 'entry3', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}]}]}

        self.assertDictEqual(result_string[1], expected_element)

        result_string = '<div>' + result_string[0] + '</div>'

        result_html = etree.fromstring(result_string)
        expected_html = self.sequence_data_handler.get_html2(xsd_files + '.reload')

        self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_multiple_unbounded(self):
        xsd_files = join('multiple', 'unbounded')
        xsd_tree = self.sequence_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.sequence_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_sequence(self.request, xsd_element, xsd_tree, '', full_path='/root',
                                          edit_data_tree=edit_data_tree)

        expected_element = {'value': None, 'tag': 'sequence', 'occurs': (2.0, 1, float('infinity')), 'module': None, 'children': [{'value': None, 'tag': 'sequence-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'choice', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'choice-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'element', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': 'entry0', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}, {'value': None, 'tag': 'element', 'occurs': (1, 2, 1), 'module': None, 'children': [{'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': 'entry4', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}, {'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': 'entry8', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}]}]}, {'value': None, 'tag': 'element', 'occurs': (1, 3, 1), 'module': None, 'children': [{'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': 'entry1', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}, {'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': 'entry5', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}, {'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': 'entry9', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}, {'value': None, 'tag': 'sequence', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': None, 'tag': 'element', 'occurs': (1, 3, 1), 'module': None, 'children': [{'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': 'entry2', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}, {'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': 'entry6', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}, {'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': 'entry10', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}, {'value': None, 'tag': 'element', 'occurs': (1, 3, 1), 'module': None, 'children': [{'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': 'entry3', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}, {'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': 'entry7', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}, {'value': None, 'tag': 'elem-iter', 'occurs': (1, 1, 1), 'module': None, 'children': [{'value': 'entry11', 'tag': 'input', 'occurs': (1, 1, 1), 'module': None, 'children': []}]}]}]}]}]}

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.sequence_data_handler.get_html2(xsd_files + '.reload')

        self.assertTrue(are_equals(result_html, expected_html))


class ParserGenerateSequenceAbsentTestSuite(TestCase):
    """
    """

    def setUp(self):
        sequence_data = join('curate', 'tests', 'data', 'parser', 'sequence_absent')
        self.sequence_data_handler = DataHandler(sequence_data)

        self.request = HttpRequest()
        engine = import_module('django.contrib.sessions.backends.db')
        session_key = None
        self.request.session = engine.SessionStore(session_key)

        self.maxDiff = None

        self.request.session['curate_edit'] = False  # Data edition
        self.request.session['nb_html_tags'] = 0
        self.request.session['mapTagID'] = {}
        self.request.session['nbChoicesID'] = 0
        self.request.session['defaultPrefix'] = 'test'

    def test_create_element_basic(self):
        xsd_tree = self.sequence_data_handler.get_xsd2(join('element', 'basic'))
        xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]

        result_string = generate_sequence_absent(self.request, xsd_element, xsd_tree, '')
        # print result_string

        expected_element = {
            'tag': 'sequence-iter',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'element',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'elem-iter',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'input',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': '',
                                    'children': []
                                }
                            ]
                        }

                    ]
                }

            ]
        }

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.sequence_data_handler.get_html2(join('element', 'basic'))

        self.assertTrue(are_equals(result_html, expected_html))

    def test_create_element_unbounded(self):
        xsd_tree = self.sequence_data_handler.get_xsd2(join('element', 'unbounded'))
        xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]

        result_string = generate_sequence_absent(self.request, xsd_element, xsd_tree, '')
        # print result_string

        expected_element = {
            'tag': 'sequence-iter',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'element',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'elem-iter',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'input',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': '',
                                    'children': []
                                }
                            ]
                        }

                    ]
                }

            ]
        }

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.sequence_data_handler.get_html2(join('element', 'unbounded'))

        self.assertTrue(are_equals(result_html, expected_html))

    # def test_create_group_basic(self):
    #     # FIXME change test and implement group support on the parser
    #     xsd_tree = self.sequence_data_handler.get_xsd2(join('group', 'basic'))
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     result_string = generate_sequence_absent(self.request, xsd_element, xsd_tree, '')
    #     self.assertEqual(result_string, "")
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.sequence_data_handler.get_html2(join('element', 'element'))
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))

    # def test_create_group_unbounded(self):
    #     xsd_tree = self.sequence_data_handler.get_xsd2(join('group', 'unbounded'))
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     result_string = generate_sequence_absent(self.request, xsd_element, xsd_tree, '')
    #     # print result_string
    #     self.assertEqual(result_string, "")
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.sequence_data_handler.get_html2(join('group', 'unbounded'))
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))

    def test_create_choice_basic(self):
        xsd_tree = self.sequence_data_handler.get_xsd2(join('choice', 'basic'))
        xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]

        result_string = generate_sequence_absent(self.request, xsd_element, xsd_tree, '')
        # print result_string

        expected_element = {
            'tag': 'sequence-iter',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'choice',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'choice-iter',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'element',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': [
                                        {
                                            'tag': 'elem-iter',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': None,
                                            'children': [
                                                {
                                                    'tag': 'input',
                                                    'occurs': (1, 1, 1),
                                                    'module': None,
                                                    'value': '',
                                                    'children': []
                                                }
                                            ]
                                        }

                                    ]
                                },
                                {
                                    'tag': 'element',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': []
                                },
                            ]
                        }

                    ]
                }

            ]
        }

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.sequence_data_handler.get_html2(join('choice', 'basic'))

        self.assertTrue(are_equals(result_html, expected_html))

    def test_create_choice_unbounded(self):
        xsd_tree = self.sequence_data_handler.get_xsd2(join('choice', 'unbounded'))
        xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]

        result_string = generate_sequence_absent(self.request, xsd_element, xsd_tree, '')
        # print result_string

        expected_element = {
            'tag': 'sequence-iter',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'choice',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'choice-iter',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'element',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': [
                                        {
                                            'tag': 'elem-iter',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': None,
                                            'children': [
                                                {
                                                    'tag': 'input',
                                                    'occurs': (1, 1, 1),
                                                    'module': None,
                                                    'value': '',
                                                    'children': []
                                                }
                                            ]
                                        }

                                    ]
                                },
                                {
                                    'tag': 'element',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': []
                                },
                            ]
                        }

                    ]
                }

            ]
        }

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.sequence_data_handler.get_html2(join('choice', 'unbounded'))

        self.assertTrue(are_equals(result_html, expected_html))

    def test_create_sequence_basic(self):
        xsd_tree = self.sequence_data_handler.get_xsd2(join('sequence', 'basic'))
        xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]

        result_string = generate_sequence_absent(self.request, xsd_element, xsd_tree, '')
        # print result_string

        expected_element = {
            'tag': 'sequence-iter',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'sequence',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'element',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'elem-iter',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': [
                                        {
                                            'tag': 'input',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': '',
                                            'children': []
                                        }
                                    ]
                                }

                            ]
                        }
                    ]
                }

            ]
        }

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.sequence_data_handler.get_html2(join('sequence', 'basic'))

        self.assertTrue(are_equals(result_html, expected_html))

    def test_create_sequence_unbounded(self):
        xsd_tree = self.sequence_data_handler.get_xsd2(join('sequence', 'unbounded'))
        xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]

        result_string = generate_sequence_absent(self.request, xsd_element, xsd_tree, '')
        # print result_string

        expected_element = {
            'tag': 'sequence-iter',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'sequence',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'element',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'elem-iter',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': [
                                        {
                                            'tag': 'input',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': '',
                                            'children': []
                                        }
                                    ]
                                }

                            ]
                        }
                    ]
                }

            ]
        }

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.sequence_data_handler.get_html2(join('sequence', 'unbounded'))

        self.assertTrue(are_equals(result_html, expected_html))

    # def test_create_any_basic(self):
    #     # FIXME How do we want to handle any's?
    #     xsd_tree = self.sequence_data_handler.get_xsd2(join('any', 'basic'))
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     result_string = generate_sequence_absent(self.request, xsd_element, xsd_tree, '')
    #     self.assertEqual(result_string, '')
    #
    # def test_create_any_unbounded(self):
    #     # FIXME How do we want to handle any's?
    #     xsd_tree = self.sequence_data_handler.get_xsd2(join('any', 'unbounded'))
    #     xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]
    #
    #     result_string = generate_sequence_absent(self.request, xsd_element, xsd_tree, '')
    #     # print result_string
    #     self.assertEqual(result_string, '')
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.sequence_data_handler.get_html2(join('any', 'unbounded'))
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))

    def test_create_multiple_basic(self):
        xsd_tree = self.sequence_data_handler.get_xsd2(join('multiple', 'basic'))
        xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]

        result_string = generate_sequence_absent(self.request, xsd_element, xsd_tree, '')
        # print result_string

        expected_element = {
            'tag': 'sequence-iter',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'choice',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'choice-iter',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'element',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': [
                                        {
                                            'tag': 'elem-iter',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': None,
                                            'children': [
                                                {
                                                    'tag': 'input',
                                                    'occurs': (1, 1, 1),
                                                    'module': None,
                                                    'value': '',
                                                    'children': []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    'tag': 'element',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': []
                                }

                            ]
                        }
                    ]
                },
                {
                    'tag': 'element',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'elem-iter',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'input',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': '',
                                    'children': []
                                }
                            ]
                        }

                    ]
                },
                {
                    'tag': 'sequence',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'element',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'elem-iter',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': [
                                        {
                                            'tag': 'input',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': '',
                                            'children': []
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            'tag': 'element',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'elem-iter',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': [
                                        {
                                            'tag': 'input',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': '',
                                            'children': []
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }

            ]
        }

        self.assertDictEqual(result_string[1], expected_element)

        result_string = '<div>' + result_string[0] + '</div>'

        result_html = etree.fromstring(result_string)
        expected_html = self.sequence_data_handler.get_html2(join('multiple', 'basic'))

        self.assertTrue(are_equals(result_html, expected_html))

    def test_create_multiple_valid(self):
        xsd_tree = self.sequence_data_handler.get_xsd2(join('multiple', 'unbounded'))
        xsd_element = xsd_tree.xpath('/schema/complexType/sequence')[0]

        result_string = generate_sequence_absent(self.request, xsd_element, xsd_tree, '')
        # print result_string

        expected_element = {
            'tag': 'sequence-iter',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'choice',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'choice-iter',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'element',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': [
                                        {
                                            'tag': 'elem-iter',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': None,
                                            'children': [
                                                {
                                                    'tag': 'input',
                                                    'occurs': (1, 1, 1),
                                                    'module': None,
                                                    'value': '',
                                                    'children': []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    'tag': 'element',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': []
                                }

                            ]
                        }
                    ]
                },
                {
                    'tag': 'element',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'elem-iter',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'input',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': '',
                                    'children': []
                                }
                            ]
                        }

                    ]
                },
                {
                    'tag': 'sequence',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'element',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'elem-iter',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': [
                                        {
                                            'tag': 'input',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': '',
                                            'children': []
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            'tag': 'element',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'elem-iter',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': [
                                        {
                                            'tag': 'input',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': '',
                                            'children': []
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }

            ]
        }

        self.assertDictEqual(result_string[1], expected_element)

        result_string = '<div>' + result_string[0] + '</div>'

        result_html = etree.fromstring(result_string)
        expected_html = self.sequence_data_handler.get_html2(join('multiple', 'unbounded'))

        self.assertTrue(are_equals(result_html, expected_html))


class ParserGenerateChoiceTestSuite(TestCase):
    """
    """

    def setUp(self):
        choice_data = join('curate', 'tests', 'data', 'parser', 'choice')
        self.choice_data_handler = DataHandler(choice_data)

        self.maxDiff = None

        self.request = HttpRequest()
        engine = import_module('django.contrib.sessions.backends.db')
        session_key = None
        self.request.session = engine.SessionStore(session_key)

        self.request.session['curate_edit'] = False  # Data edition
        self.request.session['nb_html_tags'] = 0
        self.request.session['mapTagID'] = {}
        self.request.session['nbChoicesID'] = 0
        self.request.session['defaultPrefix'] = 'test'

    def test_create_element_basic(self):
        xsd_files = join('element', 'basic')
        xsd_tree = self.choice_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/complexType/choice')[0]

        result_string = generate_choice(self.request, xsd_element, xsd_tree, '', full_path='')
        # print result_string

        expected_element = {
            'tag': 'choice',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'choice-iter',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'element',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'elem-iter',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': [
                                        {
                                            'tag': 'input',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': '',
                                            'children': []
                                        },
                                    ]
                                },
                            ]
                        },
                        {
                            'tag': 'element',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': []
                        }
                    ]
                }

            ]
        }

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.choice_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    def test_create_element_unbounded(self):
        xsd_files = join('element', 'unbounded')
        xsd_tree = self.choice_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/complexType/choice')[0]

        result_string = generate_choice(self.request, xsd_element, xsd_tree, '', full_path='')
        # print result_string

        expected_element = {
            'tag': 'choice',
            'occurs': (2., 2., float('infinity')),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'choice-iter',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'element',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'elem-iter',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': [
                                        {
                                            'tag': 'input',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': '',
                                            'children': []
                                        },
                                    ]
                                },
                            ]
                        },
                        {
                            'tag': 'element',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': []
                        }
                    ]
                },
                {
                    'tag': 'choice-iter',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'element',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'elem-iter',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': [
                                        {
                                            'tag': 'input',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': '',
                                            'children': []
                                        },
                                    ]
                                },
                            ]
                        },
                        {
                            'tag': 'element',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': []
                        }
                    ]
                },

            ]
        }

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.choice_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    # FIXME group test are not good since it is not supported by the parser
    # def test_create_group_basic(self):
    #     xsd_files = join('group', 'basic')
    #     xsd_tree = self.choice_data_handler.get_xsd2(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType/choice')[0]
    #
    #     result_string = generate_choice(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.choice_data_handler.get_html2(xsd_files)
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_group_unbounded(self):
    #     xsd_files = join('group', 'unbounded')
    #     xsd_tree = self.choice_data_handler.get_xsd2(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType/choice')[0]
    #
    #     result_string = generate_choice(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.choice_data_handler.get_html2(xsd_files)
    #
    #     self.assertTrue(are_equals(result_html, expected_html))

    # FIXME choice test are not good since it is not supported by the parser
    # def test_create_choice_basic(self):
    #     xsd_files = join('choice', 'basic')
    #     xsd_tree = self.choice_data_handler.get_xsd2(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType/choice')[0]
    #
    #     result_string = generate_choice(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.choice_data_handler.get_html2(xsd_files)
    #
    #     self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_create_choice_unbounded(self):
    #     xsd_files = join('choice', 'unbounded')
    #     xsd_tree = self.choice_data_handler.get_xsd2(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType/choice')[0]
    #
    #     result_string = generate_choice(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #
    #     result_html = etree.fromstring(result_string)
    #     expected_html = self.choice_data_handler.get_html2(xsd_files)
    #
    #     self.assertTrue(are_equals(result_html, expected_html))

    def test_create_sequence_basic(self):
        xsd_files = join('sequence', 'basic')
        xsd_tree = self.choice_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/complexType/choice')[0]

        result_string = generate_choice(self.request, xsd_element, xsd_tree, '', full_path='')
        # print result_string

        expected_element = {
            'tag': 'choice',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'choice-iter',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'sequence',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'element',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': [
                                        {
                                            'tag': 'elem-iter',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': None,
                                            'children': [
                                                {
                                                    'tag': 'input',
                                                    'occurs': (1, 1, 1),
                                                    'module': None,
                                                    'value': '',
                                                    'children': []
                                                },
                                            ]
                                        },
                                    ]
                                },
                            ]
                        },
                        {
                            'tag': 'sequence',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [

                                {
                                    'tag': 'element',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': []
                                },
                            ]
                        }
                    ]
                }

            ]
        }

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.choice_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    def test_create_sequence_unbounded(self):
        xsd_files = join('sequence', 'unbounded')
        xsd_tree = self.choice_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/complexType/choice')[0]

        result_string = generate_choice(self.request, xsd_element, xsd_tree, '', full_path='')
        # print result_string

        expected_element = {
            'value': None,
            'tag': 'choice',
            'occurs': (2.0, 2.0, float('infinity')),
            'module': None,
            'children': [
                {
                    'value': None,
                    'tag': 'choice-iter',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'children': [
                        {
                            'value': None,
                            'tag': 'sequence',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'children': [
                                {
                                    'value': None,
                                    'tag': 'element',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'children': [
                                        {
                                            'value': None,
                                            'tag': 'elem-iter',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'children': [
                                                {
                                                    'value': '',
                                                    'tag': 'input',
                                                    'occurs': (1, 1, 1),
                                                    'module': None,
                                                    'children': []
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            'value': None,
                            'tag': 'sequence',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'children': [
                                {
                                    'value': None,
                                    'tag': 'element',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'children': []
                                }
                            ]
                        }
                    ]
                },
                {
                    'value': None,
                    'tag': 'choice-iter',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'children': [
                        {
                            'value': None,
                            'tag': 'sequence',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'children': [
                                {
                                    'value': None,
                                    'tag': 'element',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'children': [
                                        {
                                            'value': None,
                                            'tag': 'elem-iter',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'children': [
                                                {
                                                    'value': '',
                                                    'tag': 'input',
                                                    'occurs': (1, 1, 1),
                                                    'module': None,
                                                    'children': []
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            'value': None,
                            'tag': 'sequence',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'children': [
                                {
                                    'value': None,
                                    'tag': 'element',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'children': []
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.choice_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    # TODO implement later
    # def test_create_any_basic(self):
    #     pass
    #
    # def test_create_any_unbounded(self):
    #     pass

    def test_reload_element_basic(self):
        xsd_files = join('element', 'basic')
        xsd_tree = self.choice_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/complexType/choice')[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.choice_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_choice(self.request, xsd_element, xsd_tree, '', full_path='/root',
                                        edit_data_tree=edit_data_tree)
        # print result_string

        expected_element = {
            'tag': 'choice',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'choice-iter',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'element',
                            'occurs': (1, 0, 1),
                            'module': None,
                            'value': None,
                            'children': []
                        },
                        {
                            'tag': 'element',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'elem-iter',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': [
                                        {
                                            'tag': 'input',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': 'entry0',
                                            'children': []
                                        },
                                    ]
                                },
                            ]
                        },
                    ]
                }

            ]
        }

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.choice_data_handler.get_html2(xsd_files + '.reload')

        self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_element_unbounded(self):
        # FIXME correct the bug here
        xsd_files = join('element', 'unbounded')
        xsd_tree = self.choice_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/complexType/choice')[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.choice_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_choice(self.request, xsd_element, xsd_tree, '', full_path='/root',
                                        edit_data_tree=edit_data_tree)
        # print result_string

        expected_element = {
            'value': None,
            'tag': 'choice',
            'occurs': (2.0, 1, float('infinity')),
            'module': None,
            'children': [
                {
                    'value': None,
                    'tag': 'choice-iter',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'children': [
                        {
                            'value': None,
                            'tag': 'element',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'children': [
                                {
                                    'value': None,
                                    'tag': 'elem-iter',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'children': [
                                        {
                                            'value': 'entry1',
                                            'tag': 'input',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'children': []
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            'value': None,
                            'tag': 'element',
                            'occurs': (1, 2, 1),
                            'module': None,
                            'children': [
                                {
                                    'value': None,
                                    'tag': 'elem-iter',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'children': [
                                        {
                                            'value': 'entry0',
                                            'tag': 'input',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'children': []
                                        }
                                    ]
                                },
                                {
                                    'value': None,
                                    'tag': 'elem-iter',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'children': [
                                        {
                                            'value': 'entry2',
                                            'tag': 'input',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'children': []
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.choice_data_handler.get_html2(xsd_files + '.reload')

        self.assertTrue(are_equals(result_html, expected_html))

    # TODO implement later
    # def test_reload_group_basic(self):
    #     xsd_files = join('element', 'basic')
    #     xsd_tree = self.choice_data_handler.get_xsd2(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType/choice')[0]
    #
    #     self.request.session['curate_edit'] = True
    #
    #     xml_tree = self.choice_data_handler.get_xml(xsd_files)
    #     xml_data = etree.tostring(xml_tree)
    #
    #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
    #     etree.set_default_parser(parser=clean_parser)
    #     # load the XML tree from the text
    #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
    #     result_string = generate_choice(self.request, xsd_element, xsd_tree, '', full_path='/root',
    #                                    edit_data_tree=edit_data_tree)
    #     print result_string
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.choice_data_handler.get_html2(xsd_files + '.reload')
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))

    # def test_reload_group_unbounded(self):
    #     xsd_files = join('element', 'basic')
    #     xsd_tree = self.choice_data_handler.get_xsd2(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType/choice')[0]
    #
    #     self.request.session['curate_edit'] = True
    #
    #     xml_tree = self.choice_data_handler.get_xml(xsd_files)
    #     xml_data = etree.tostring(xml_tree)
    #
    #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
    #     etree.set_default_parser(parser=clean_parser)
    #     # load the XML tree from the text
    #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
    #     result_string = generate_choice(self.request, xsd_element, xsd_tree, '', full_path='/root',
    #                                    edit_data_tree=edit_data_tree)
    #     print result_string
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.choice_data_handler.get_html2(xsd_files + '.reload')
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_reload_choice_basic(self):
    #     xsd_files = join('element', 'basic')
    #     xsd_tree = self.choice_data_handler.get_xsd2(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType/choice')[0]
    #
    #     self.request.session['curate_edit'] = True
    #
    #     xml_tree = self.choice_data_handler.get_xml(xsd_files)
    #     xml_data = etree.tostring(xml_tree)
    #
    #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
    #     etree.set_default_parser(parser=clean_parser)
    #     # load the XML tree from the text
    #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
    #     result_string = generate_choice(self.request, xsd_element, xsd_tree, '', full_path='/root',
    #                                    edit_data_tree=edit_data_tree)
    #     print result_string
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.choice_data_handler.get_html2(xsd_files + '.reload')
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))
    #
    # def test_reload_choice_unbounded(self):
    #     xsd_files = join('element', 'basic')
    #     xsd_tree = self.choice_data_handler.get_xsd2(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType/choice')[0]
    #
    #     self.request.session['curate_edit'] = True
    #
    #     xml_tree = self.choice_data_handler.get_xml(xsd_files)
    #     xml_data = etree.tostring(xml_tree)
    #
    #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
    #     etree.set_default_parser(parser=clean_parser)
    #     # load the XML tree from the text
    #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
    #     result_string = generate_choice(self.request, xsd_element, xsd_tree, '', full_path='/root',
    #                                    edit_data_tree=edit_data_tree)
    #     print result_string
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.choice_data_handler.get_html2(xsd_files + '.reload')
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_sequence_basic(self):
        xsd_files = join('sequence', 'basic')
        xsd_tree = self.choice_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/complexType/choice')[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.choice_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_choice(self.request, xsd_element, xsd_tree, '', full_path='/root',
                                        edit_data_tree=edit_data_tree)
        # print result_string

        expected_element = {
            'value': None,
            'tag': 'choice',
            'occurs': (1, 1, 1),
            'module': None,
            'children': [
                {
                    'value': None,
                    'tag': 'choice-iter',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'children': [
                        {
                            'value': None,
                            'tag': 'sequence',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'children': [
                                {
                                    'value': None,
                                    'tag': 'element',
                                    'occurs': (1, 0, 1),
                                    'module': None,
                                    'children': []
                                }
                            ]
                        },
                        {
                            'value': None,
                            'tag': 'sequence',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'children': [
                                {
                                    'value': None,
                                    'tag': 'element',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'children': [
                                        {
                                            'value': None,
                                            'tag': 'elem-iter',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'children': [
                                                {
                                                    'value': 'entry0',
                                                    'tag': 'input',
                                                    'occurs': (1, 1, 1),
                                                    'module': None,
                                                    'children': []
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.choice_data_handler.get_html2(xsd_files + '.reload')

        self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_sequence_unbounded(self):
        # fixme correct the bug
        xsd_files = join('sequence', 'unbounded')
        xsd_tree = self.choice_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/complexType/choice')[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.choice_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_choice(self.request, xsd_element, xsd_tree, '', full_path='/root',
                                        edit_data_tree=edit_data_tree)
        # print result_string

        expected_element = {
            'value': None,
            'tag': 'choice',
            'occurs': (2.0, 1, float('infinity')),
            'module': None,
            'children': [
                {
                    'value': None,
                    'tag': 'choice-iter',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'children': [
                        {
                            'value': None,
                            'tag': 'sequence',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'children': [
                                {
                                    'value': None,
                                    'tag': 'element',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'children': [
                                        {
                                            'value': None,
                                            'tag': 'elem-iter',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'children': [
                                                {
                                                    'value': 'entry2',
                                                    'tag': 'input',
                                                    'occurs': (1, 1, 1),
                                                    'module': None,
                                                    'children': []
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            'value': None,
                            'tag': 'sequence',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'children': [
                                {
                                    'value': None,
                                    'tag': 'element',
                                    'occurs': (1, 2, 1),
                                    'module': None,
                                    'children': [
                                        {
                                            'value': None,
                                            'tag': 'elem-iter',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'children': [
                                                {
                                                    'value': 'entry0',
                                                    'tag': 'input',
                                                    'occurs': (1, 1, 1),
                                                    'module': None,
                                                    'children': []
                                                }
                                            ]
                                        },
                                        {
                                            'value': None,
                                            'tag': 'elem-iter',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'children': [
                                                {
                                                    'value': 'entry1',
                                                    'tag': 'input',
                                                    'occurs': (1, 1, 1),
                                                    'module': None,
                                                    'children': []
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.choice_data_handler.get_html2(xsd_files + '.reload')

        self.assertTrue(are_equals(result_html, expected_html))

    # TODO implement later
    # def test_reload_any_basic(self):
    #     pass
    #
    # def test_reload_any_unbounded(self):
    #     pass


class ParserGenerateSimpleTypeTestSuite(TestCase):
    """
    """

    def setUp(self):
        simple_type_data = join('curate', 'tests', 'data', 'parser', 'simple_type')
        self.simple_type_data_handler = DataHandler(simple_type_data)

        self.maxDiff = None

        self.request = HttpRequest()
        engine = import_module('django.contrib.sessions.backends.db')
        session_key = None
        self.request.session = engine.SessionStore(session_key)

        self.request.session['curate_edit'] = False  # Data edition
        self.request.session['nb_html_tags'] = 0
        self.request.session['mapTagID'] = {}
        self.request.session['nbChoicesID'] = 0
        self.request.session['defaultPrefix'] = 'test'

    def test_create_restriction(self):
        xsd_files = join('restriction', 'basic')
        xsd_tree = self.simple_type_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/simpleType')[0]

        result_string = generate_simple_type(self.request, xsd_element, xsd_tree, '', full_path='')
        # print result_string

        expected_dict = {
            'tag': 'simple_type',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'restriction',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'enumeration',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': 'child_0',
                            'children': []
                        },
                        {
                            'tag': 'enumeration',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': 'child_1',
                            'children': []
                        },
                        {
                            'tag': 'enumeration',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': 'child_2',
                            'children': []
                        }
                    ]
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_dict)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.simple_type_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    def test_create_list(self):
        xsd_files = join('list', 'basic')
        xsd_tree = self.simple_type_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/simpleType')[0]

        result_string = generate_simple_type(self.request, xsd_element, xsd_tree, '', full_path='')
        # print result_string

        expected_dict = {
            'tag': 'simple_type',
            'occurs': (1, 1, 1),
            'value': None,
            'module': None,
            'children': [
                {
                    'tag': 'list',
                    'occurs': (1, 1, 1),
                    'value': '',
                    'module': None,
                    'children': []
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_dict)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.simple_type_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    # FIXME Union test is not good cause it has not been implemented on the server
    # def test_create_union(self):
    #     xsd_files = join('union', 'basic')
    #     xsd_tree = self.simple_type_data_handler.get_xsd2(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/simpleType')[0]
    #
    #     result_string = generate_simple_type(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #     self.assertEqual(result_string, '')
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.simple_type_data_handler.get_html2(xsd_files)
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_restriction(self):
        xsd_files = join('restriction', 'basic')
        xsd_tree = self.simple_type_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/simpleType')[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.simple_type_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_simple_type(self.request, xsd_element, xsd_tree, '', full_path='/root',
                                             edit_data_tree=edit_data_tree)
        # print result_string

        expected_dict = {
            'tag': 'simple_type',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'restriction',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'enumeration',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': 'child_0',
                            'children': []
                        },
                        {
                            'tag': 'enumeration/selected',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': 'child_1',
                            'children': []
                        },
                        {
                            'tag': 'enumeration',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': 'child_2',
                            'children': []
                        }
                    ]
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_dict)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.simple_type_data_handler.get_html2(xsd_files + '.reload')

        self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_list(self):
        # fixme correct bugs
        xsd_files = join('list', 'basic')
        xsd_tree = self.simple_type_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/simpleType')[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.simple_type_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_simple_type(self.request, xsd_element, xsd_tree, '', full_path='/root',
                                             edit_data_tree=edit_data_tree)
        # print result_string

        expected_dict = {
            'tag': 'simple_type',
            'occurs': (1, 1, 1),
            'value': None,
            'module': None,
            'children': [
                {
                    'tag': 'list',
                    'occurs': (1, 1, 1),
                    'value': '',
                    'module': None,
                    'children': []
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_dict)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.simple_type_data_handler.get_html2(xsd_files + '.reload')

        self.assertTrue(are_equals(result_html, expected_html))

    # fixme support for union is not there yet
    # def test_reload_union(self):
    #     xsd_files = join('restriction', 'basic')
    #     xsd_tree = self.simple_type_data_handler.get_xsd2(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/simpleType')[0]
    #
    #     self.request.session['curate_edit'] = True
    #
    #     xml_tree = self.simple_type_data_handler.get_xml(xsd_files)
    #     xml_data = etree.tostring(xml_tree)
    #
    #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
    #     etree.set_default_parser(parser=clean_parser)
    #     # load the XML tree from the text
    #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
    #     result_string = generate_simple_type(self.request, xsd_element, xsd_tree, '', full_path='/root',
    #                                        edit_data_tree=edit_data_tree)
    #     print result_string
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.simple_type_data_handler.get_html2(xsd_files + '.reload')
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))


class ParserGenerateComplexTypeTestSuite(TestCase):
    """
    """

    def setUp(self):
        complex_type_data = join('curate', 'tests', 'data', 'parser', 'complex_type')
        self.complex_type_data_handler = DataHandler(complex_type_data)

        self.maxDiff = None

        self.request = HttpRequest()
        engine = import_module('django.contrib.sessions.backends.db')
        session_key = None
        self.request.session = engine.SessionStore(session_key)

        self.request.session['curate_edit'] = False  # Data edition
        self.request.session['nb_html_tags'] = 0
        self.request.session['mapTagID'] = {}
        self.request.session['nbChoicesID'] = 0
        self.request.session['defaultPrefix'] = 'test'

    # FIXME simpleContent not correctly supported
    def test_create_simple_content(self):
        xsd_files = join('simple_content', 'basic')
        xsd_tree = self.complex_type_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/complexType')[0]

        result_string = generate_complex_type(self.request, xsd_element, xsd_tree, '', full_path='')
        # print result_string

        expected_element = {
            'tag': 'complex_type',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'simple_content',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'extension',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'input',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': '',
                                    'children': [

                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.complex_type_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    # FIXME complexContent not properly supported
    def test_create_complex_content(self):
        xsd_files = join('complex_content', 'basic')
        xsd_tree = self.complex_type_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/complexType')[0]

        result_string = generate_complex_type(self.request, xsd_element, xsd_tree, '', full_path='')
        # print result_string

        expected_element = {
            'tag': 'complex_type',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': []
        }

        self.assertDictEqual(result_string[1], expected_element)

        self.assertEqual(result_string[0], '')

        # result_html = etree.fromstring(result_string)
        # expected_html = self.complex_type_data_handler.get_html2(xsd_files)
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    # FIXME group not properly supported
    def test_create_group(self):
        xsd_files = join('group', 'basic')
        xsd_tree = self.complex_type_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/complexType')[0]

        result_string = generate_complex_type(self.request, xsd_element, xsd_tree, '', full_path='')
        # print result_string
        self.assertEqual(result_string[0], '')

        expected_element = {
            'tag': 'complex_type',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': []
        }

        self.assertDictEqual(result_string[1], expected_element)

        # result_html = etree.fromstring(result_string)
        # expected_html = self.complex_type_data_handler.get_html2(xsd_files)
        #
        # self.assertTrue(are_equals(result_html, expected_html))

    def test_create_all(self):
        xsd_files = join('all', 'basic')
        xsd_tree = self.complex_type_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/complexType')[0]

        result_string = generate_complex_type(self.request, xsd_element, xsd_tree, '', full_path='')

        # print result_string

        expected_element = {
            'tag': 'complex_type',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'all',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'element',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'elem-iter',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': [
                                        {
                                            'tag': 'input',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': '',
                                            'children': []
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            'tag': 'element',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'elem-iter',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': [
                                        {
                                            'tag': 'input',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': '',
                                            'children': []
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_element)

        result_string = '<div>' + result_string[0] + '</div>'

        result_html = etree.fromstring(result_string)
        expected_html = self.complex_type_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    def test_create_choice(self):
        xsd_files = join('choice', 'basic')
        xsd_tree = self.complex_type_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/complexType')[0]

        result_string = generate_complex_type(self.request, xsd_element, xsd_tree, '', full_path='')
        # print result_string

        expected_element = {
            'tag': 'complex_type',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'choice',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'choice-iter',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'element',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': [
                                        {
                                            'tag': 'elem-iter',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': None,
                                            'children': [
                                                {
                                                    'tag': 'input',
                                                    'occurs': (1, 1, 1),
                                                    'module': None,
                                                    'value': '',
                                                    'children': []
                                                }
                                            ]
                                        }
                                    ]
                                },
                                {
                                    'tag': 'element',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': []
                                },
                            ]
                        }
                    ]
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.complex_type_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    def test_create_sequence(self):
        xsd_files = join('sequence', 'basic')
        xsd_tree = self.complex_type_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/complexType')[0]

        result_string = generate_complex_type(self.request, xsd_element, xsd_tree, '', full_path='')

        # print result_string

        expected_element = {
            'tag': 'complex_type',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'sequence',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'element',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'elem-iter',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': [
                                        {
                                            'tag': 'input',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': '',
                                            'children': []
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            'tag': 'element',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'elem-iter',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': [
                                        {
                                            'tag': 'input',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': '',
                                            'children': []
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_element)

        result_string = '<div>' + result_string[0] + '</div>'

        result_html = etree.fromstring(result_string)
        expected_html = self.complex_type_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    def test_create_attribute(self):
        xsd_files = join('attribute', 'basic')
        xsd_tree = self.complex_type_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/complexType')[0]

        result_string = generate_complex_type(self.request, xsd_element, xsd_tree, '', full_path='')
        # print result_string

        expected_element = {
            'tag': 'complex_type',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'attribute',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'elem-iter',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'input',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': '',
                                    'children': []
                                },
                            ]
                        },
                    ]
                },
            ]
        }

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.complex_type_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    # FIXME attribute group is not yet supported
    # def test_create_attribute_group(self):
    #     xsd_files = join('attribute_group', 'basic')
    #     xsd_tree = self.complex_type_data_handler.get_xsd2(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType')[0]
    #
    #     result_string = generate_complex_type(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #     self.assertEqual(result_string, '')
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.complex_type_data_handler.get_html2(xsd_files)
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))

    # FIXME any attribute is not yet supported
    # def test_create_any_attribute(self):
    #     xsd_files = join('any_attribute', 'basic')
    #     xsd_tree = self.complex_type_data_handler.get_xsd2(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType')[0]
    #
    #     result_string = generate_complex_type(self.request, xsd_element, xsd_tree, '', full_path='')
    #     # print result_string
    #     self.assertEqual(result_string, '')
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.complex_type_data_handler.get_html2(xsd_files)
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))

    def test_create_multiple(self):
        xsd_files = join('multiple', 'basic')
        xsd_tree = self.complex_type_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/complexType')[0]

        result_string = generate_complex_type(self.request, xsd_element, xsd_tree, '', full_path='')

        expected_element = {
            'tag': 'complex_type',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                # FIXME Order is wrong
                {
                    'tag': 'attribute',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'elem-iter',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'input',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': '',
                                    'children': []
                                },
                            ]
                        },
                    ]
                },
                {
                    'tag': 'attribute',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'elem-iter',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'input',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': '',
                                    'children': []
                                },
                            ]
                        },
                    ]
                },
                {
                    'tag': 'sequence',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'element',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'elem-iter',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': [
                                        {
                                            'tag': 'input',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': '',
                                            'children': []
                                        },
                                    ]
                                },
                            ]
                        },
                        {
                            'tag': 'element',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'elem-iter',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': [
                                        {
                                            'tag': 'input',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': '',
                                            'children': []
                                        },
                                    ]
                                },
                            ]
                        },
                    ]
                },
            ]
        }

        self.assertDictEqual(result_string[1], expected_element)

        result_string = '<div>' + result_string[0] + '</div>'
        # print result_string

        result_html = etree.fromstring(result_string)
        expected_html = self.complex_type_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_simple_content(self):
        xsd_files = join('simple_content', 'basic')
        xsd_tree = self.complex_type_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/complexType')[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.complex_type_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_complex_type(self.request, xsd_element, xsd_tree, '', full_path='/root',
                                              edit_data_tree=edit_data_tree)
        # print result_string

        expected_element = {
            'tag': 'complex_type',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'simple_content',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'extension',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'input',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': '0',
                                    'children': [

                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.complex_type_data_handler.get_html2(xsd_files + '.reload')

        self.assertTrue(are_equals(result_html, expected_html))

    # fixme complex content not implemented
    # def test_reload_complex_content(self):
    #     xsd_files = join('simple_content', 'basic')
    #     xsd_tree = self.complex_type_data_handler.get_xsd2(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType')[0]
    #
    #     self.request.session['curate_edit'] = True
    #
    #     xml_tree = self.complex_type_data_handler.get_xml(xsd_files)
    #     xml_data = etree.tostring(xml_tree)
    #
    #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
    #     etree.set_default_parser(parser=clean_parser)
    #     # load the XML tree from the text
    #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
    #     result_string = generate_complex_type(self.request, xsd_element, xsd_tree, '', full_path='/root',
    #                                         edit_data_tree=edit_data_tree)
    #     print result_string
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.complex_type_data_handler.get_html2(xsd_files + '.reload')
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))
    #
    # fixme group not implemented
    # def test_reload_group(self):
    #     xsd_files = join('simple_content', 'basic')
    #     xsd_tree = self.complex_type_data_handler.get_xsd2(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType')[0]
    #
    #     self.request.session['curate_edit'] = True
    #
    #     xml_tree = self.complex_type_data_handler.get_xml(xsd_files)
    #     xml_data = etree.tostring(xml_tree)
    #
    #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
    #     etree.set_default_parser(parser=clean_parser)
    #     # load the XML tree from the text
    #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
    #     result_string = generate_complex_type(self.request, xsd_element, xsd_tree, '', full_path='/root',
    #                                         edit_data_tree=edit_data_tree)
    #     print result_string
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.complex_type_data_handler.get_html2(xsd_files + '.reload')
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_all(self):
        xsd_files = join('all', 'basic')
        xsd_tree = self.complex_type_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/complexType')[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.complex_type_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_complex_type(self.request, xsd_element, xsd_tree, '', full_path='/root',
                                              edit_data_tree=edit_data_tree)
        # print result_string

        expected_element = {
            'tag': 'complex_type',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'all',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'element',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'elem-iter',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': [
                                        {
                                            'tag': 'input',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': 'entry0',
                                            'children': []
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            'tag': 'element',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'elem-iter',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': [
                                        {
                                            'tag': 'input',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': 'entry1',
                                            'children': []
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }


        self.assertDictEqual(result_string[1], expected_element)

        result_string = '<div>' + result_string[0] + '</div>'

        result_html = etree.fromstring(result_string)
        expected_html = self.complex_type_data_handler.get_html2(xsd_files + '.reload')

        self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_choice(self):
        xsd_files = join('choice', 'basic')
        xsd_tree = self.complex_type_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/complexType')[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.complex_type_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_complex_type(self.request, xsd_element, xsd_tree, '', full_path='/root',
                                              edit_data_tree=edit_data_tree)
        # print result_string

        expected_element = {
            'tag': 'complex_type',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'choice',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'choice-iter',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'element',
                                    'occurs': (1, 0, 1),
                                    'module': None,
                                    'value': None,
                                    'children': []
                                },
                                {
                                    'tag': 'element',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': [
                                        {
                                            'tag': 'elem-iter',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': None,
                                            'children': [
                                                {
                                                    'tag': 'input',
                                                    'occurs': (1, 1, 1),
                                                    'module': None,
                                                    'value': 'entry0',
                                                    'children': []
                                                }
                                            ]
                                        }
                                    ]
                                },
                            ]
                        }
                    ]
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.complex_type_data_handler.get_html2(xsd_files + '.reload')

        self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_sequence(self):
        xsd_files = join('sequence', 'basic')
        xsd_tree = self.complex_type_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/complexType')[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.complex_type_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_complex_type(self.request, xsd_element, xsd_tree, '', full_path='/root',
                                              edit_data_tree=edit_data_tree)
        # print result_string

        expected_element = {
            'tag': 'complex_type',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'sequence',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'element',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'elem-iter',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': [
                                        {
                                            'tag': 'input',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': 'entry0',
                                            'children': []
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            'tag': 'element',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'elem-iter',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': [
                                        {
                                            'tag': 'input',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': 'entry1',
                                            'children': []
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_element)

        result_string = '<div>' + result_string[0] + '</div>'

        result_html = etree.fromstring(result_string)
        expected_html = self.complex_type_data_handler.get_html2(xsd_files + '.reload')

        self.assertTrue(are_equals(result_html, expected_html))

    # fixme implement attribute
    # def test_reload_attribute(self):
    #     xsd_files = join('simple_content', 'basic')
    #     xsd_tree = self.complex_type_data_handler.get_xsd2(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType')[0]
    #
    #     self.request.session['curate_edit'] = True
    #
    #     xml_tree = self.complex_type_data_handler.get_xml(xsd_files)
    #     xml_data = etree.tostring(xml_tree)
    #
    #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
    #     etree.set_default_parser(parser=clean_parser)
    #     # load the XML tree from the text
    #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
    #     result_string = generate_complex_type(self.request, xsd_element, xsd_tree, '', full_path='/root',
    #                                         edit_data_tree=edit_data_tree)
    #     print result_string
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.complex_type_data_handler.get_html2(xsd_files + '.reload')
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))
    #
    # fixme implement attributeGroup
    # def test_reload_attribute_group(self):
    #     xsd_files = join('simple_content', 'basic')
    #     xsd_tree = self.complex_type_data_handler.get_xsd2(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType')[0]
    #
    #     self.request.session['curate_edit'] = True
    #
    #     xml_tree = self.complex_type_data_handler.get_xml(xsd_files)
    #     xml_data = etree.tostring(xml_tree)
    #
    #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
    #     etree.set_default_parser(parser=clean_parser)
    #     # load the XML tree from the text
    #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
    #     result_string = generate_complex_type(self.request, xsd_element, xsd_tree, '', full_path='/root',
    #                                         edit_data_tree=edit_data_tree)
    #     print result_string
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.complex_type_data_handler.get_html2(xsd_files + '.reload')
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))
    #
    # fixme implement anyAttribute
    # def test_reload_any_attribute(self):
    #     xsd_files = join('simple_content', 'basic')
    #     xsd_tree = self.complex_type_data_handler.get_xsd2(xsd_files)
    #     xsd_element = xsd_tree.xpath('/schema/complexType')[0]
    #
    #     self.request.session['curate_edit'] = True
    #
    #     xml_tree = self.complex_type_data_handler.get_xml(xsd_files)
    #     xml_data = etree.tostring(xml_tree)
    #
    #     clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
    #     etree.set_default_parser(parser=clean_parser)
    #     # load the XML tree from the text
    #     edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
    #     result_string = generate_complex_type(self.request, xsd_element, xsd_tree, '', full_path='/root',
    #                                         edit_data_tree=edit_data_tree)
    #     print result_string
    #
    #     # result_html = etree.fromstring(result_string)
    #     # expected_html = self.complex_type_data_handler.get_html2(xsd_files + '.reload')
    #     #
    #     # self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_multiple(self):
        # fixme test broken
        xsd_files = join('multiple', 'basic')
        xsd_tree = self.complex_type_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/complexType')[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.complex_type_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_complex_type(self.request, xsd_element, xsd_tree, '', full_path='/root',
                                              edit_data_tree=edit_data_tree)
        # print result_string

        expected_element = {
            'tag': 'complex_type',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                # FIXME Order is wrong
                {
                    'tag': 'attribute',
                    'occurs': (1, 0, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'elem-iter',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': []
                        },
                    ]
                },
                {
                    'tag': 'attribute',
                    'occurs': (1, 0, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'elem-iter',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': []
                        },
                    ]
                },
                {
                    'tag': 'sequence',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': None,
                    'children': [
                        {
                            'tag': 'element',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'elem-iter',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': [
                                        {
                                            'tag': 'input',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': 'entry0',
                                            'children': []
                                        },
                                    ]
                                },
                            ]
                        },
                        {
                            'tag': 'element',
                            'occurs': (1, 1, 1),
                            'module': None,
                            'value': None,
                            'children': [
                                {
                                    'tag': 'elem-iter',
                                    'occurs': (1, 1, 1),
                                    'module': None,
                                    'value': None,
                                    'children': [
                                        {
                                            'tag': 'input',
                                            'occurs': (1, 1, 1),
                                            'module': None,
                                            'value': 'entry1',
                                            'children': []
                                        },
                                    ]
                                },
                            ]
                        },
                    ]
                },
            ]
        }

        self.assertDictEqual(result_string[1], expected_element)
        result_string = '<div>' + result_string[0] + '</div>'

        result_html = etree.fromstring(result_string)
        expected_html = self.complex_type_data_handler.get_html2(xsd_files + '.reload')

        self.assertTrue(are_equals(result_html, expected_html))


class ParserGenerateModuleTestSuite(TestCase):
    """
    """

    def setUp(self):
        module_data = join('curate', 'tests', 'data', 'parser', 'module')
        self.module_data_handler = DataHandler(module_data)

        self.request = HttpRequest()
        engine = import_module('django.contrib.sessions.backends.db')
        session_key = None
        self.request.session = engine.SessionStore(session_key)

        self.request.session['curate_edit'] = False  # Data edition
        self.request.session['curateFormData'] = "56c2261476dd090fcf002319"  # Data edition
        self.request.session['nb_html_tags'] = 0
        self.request.session['mapTagID'] = {}
        self.request.session['nbChoicesID'] = 0
        self.request.session['defaultPrefix'] = 'test'
        self.request.session['namespaces'] = {'test': ''}

    def test_create_module(self):
        xsd_files = 'registered_module'
        xsd_tree = self.module_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/complexType')[0]

        self.request.session['xmlDocTree'] = etree.tostring(xsd_tree)

        result_string = generate_module(self.request, xsd_element, '')

        result_html = etree.fromstring(result_string)
        expected_html = self.module_data_handler.get_html2('new')

        self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_module(self):
        xsd_files = 'registered_module'
        # xsd_reload_files = join('element', 'basic.reload')
        xsd_tree = self.module_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/complexType')[0]

        # self.request.session['xmlDocTree'] = etree.tostring(xsd_tree)
        self.request.session['curate_edit'] = True

        xml_data = self.module_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_data)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        # set the parser
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))

        result_string = generate_module(self.request, xsd_element, '', xsd_xpath='', xml_xpath='/module/child',
                                        edit_data_tree=edit_data_tree)

        result_html = etree.fromstring(result_string)
        expected_html = self.module_data_handler.get_html2('reload')

        self.assertTrue(are_equals(result_html, expected_html))


class ParserGenerateSimpleContentTestSuite(TestCase):
    """
    """

    def setUp(self):
        # connect to test database
        # self.db_name = "mgi_test"
        # disconnect()
        # self.connection = connect(self.db_name, port=27018)
        #
        # test_data = join('curate', 'tests', 'data', 'parser', 'simple_content')
        #
        # create_extension_data = join(test_data, 'extension', 'create')
        # self.create_extension_data_handler = DataHandler(create_extension_data)
        #
        # create_restriction_data = join(test_data, 'restriction', 'create')
        # self.create_restriction_data_handler = DataHandler(create_restriction_data)
        simple_content_data = join('curate', 'tests', 'data', 'parser', 'simple_content')
        self.simple_content_data_handler = DataHandler(simple_content_data)

        self.maxDiff = None

        self.request = HttpRequest()
        engine = import_module('django.contrib.sessions.backends.db')
        session_key = None
        self.request.session = engine.SessionStore(session_key)

        self.request.session['curate_edit'] = False  # Data edition
        self.request.session['nb_html_tags'] = 0
        self.request.session['mapTagID'] = {}
        self.request.session['nbChoicesID'] = 0
        self.request.session['defaultPrefix'] = 'test'

    def test_create_restriction(self):
        xsd_files = join('restriction', 'basic')
        xsd_tree = self.simple_content_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/complexType/simpleContent')[0]

        result_string = generate_simple_content(self.request, xsd_element, xsd_tree, '', full_path='')
        # print result_string

        expected_element = {
            'tag': 'simple_content',
            'occurs': (1, 1, 1),
            'value': None,
            'module': None,
            'children': [
                {
                    'tag': 'restriction',
                    'occurs': (1, 1, 1),
                    'value': None,
                    'module': None,
                    'children': [
                        {
                            'tag': 'enumeration',
                            'occurs': (1, 1, 1),
                            'value': 'child0',
                            'module': None,
                            'children': []
                        },
                        {
                            'tag': 'enumeration',
                            'occurs': (1, 1, 1),
                            'value': 'child1',
                            'module': None,
                            'children': []
                        }
                    ]
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.simple_content_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    # FIXME extension are not fully supported by the parser
    def test_create_extension(self):
        xsd_files = join('extension', 'basic')
        xsd_tree = self.simple_content_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/complexType/simpleContent')[0]

        result_string = generate_simple_content(self.request, xsd_element, xsd_tree, '', full_path='')
        # print result_string

        expected_element = {
            'tag': 'simple_content',
            'occurs': (1, 1, 1),
            'value': None,
            'module': None,
            'children': [
                {
                    'tag': 'extension',
                    'occurs': (1, 1, 1),
                    'value': None,
                    'module': None,
                    'children': [
                        {
                            'tag': 'input',
                            'occurs': (1, 1, 1),
                            'value': '',
                            'module': None,
                            'children': []
                        }
                    ]
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.simple_content_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_extension(self):
        xsd_files = join('extension', 'basic')
        xsd_tree = self.simple_content_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/complexType/simpleContent')[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.simple_content_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_simple_content(self.request, xsd_element, xsd_tree, '', full_path='/root',
                                                edit_data_tree=edit_data_tree)
        # print result_string
        # result_string = '<div>' + result_string + '</div>'

        expected_element = {
            'tag': 'simple_content',
            'occurs': (1, 1, 1),
            'value': None,
            'module': None,
            'children': [
                {
                    'tag': 'extension',
                    'occurs': (1, 1, 1),
                    'value': None,
                    'module': None,
                    'children': [
                        {
                            'tag': 'input',
                            'occurs': (1, 1, 1),
                            'value': 'entry0',
                            'module': None,
                            'children': []
                        }
                    ]
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.simple_content_data_handler.get_html2(xsd_files + '.reload')

        self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_restriction(self):
        xsd_files = join('restriction', 'basic')
        xsd_tree = self.simple_content_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/complexType/simpleContent')[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.simple_content_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_simple_content(self.request, xsd_element, xsd_tree, '', full_path='/root',
                                                edit_data_tree=edit_data_tree)
        # print result_string
        # result_string = '<div>' + result_string + '</div>'

        expected_element = {
            'tag': 'simple_content',
            'occurs': (1, 1, 1),
            'value': None,
            'module': None,
            'children': [
                {
                    'tag': 'restriction',
                    'occurs': (1, 1, 1),
                    'value': None,
                    'module': None,
                    'children': [
                        {
                            'tag': 'enumeration/selected',
                            'occurs': (1, 1, 1),
                            'value': 'child0',
                            'module': None,
                            'children': []
                        },
                        {
                            'tag': 'enumeration',
                            'occurs': (1, 1, 1),
                            'value': 'child1',
                            'module': None,
                            'children': []
                        }
                    ]
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.simple_content_data_handler.get_html2(xsd_files + '.reload')

        self.assertTrue(are_equals(result_html, expected_html))


class ParserGenerateRestrictionTestSuite(TestCase):
    """
    """

    def setUp(self):
        restriction_data = join('curate', 'tests', 'data', 'parser', 'restriction')
        self.restriction_data_handler = DataHandler(restriction_data)

        self.request = HttpRequest()
        engine = import_module('django.contrib.sessions.backends.db')
        session_key = None
        self.request.session = engine.SessionStore(session_key)

        self.maxDiff = None

        self.request.session['curate_edit'] = False  # Data edition
        self.request.session['nb_html_tags'] = 0
        self.request.session['mapTagID'] = {}
        self.request.session['nbChoicesID'] = 0
        self.request.session['defaultPrefix'] = 'test'

    def test_create_enumeration(self):
        xsd_files = join('enumeration', 'basic')
        xsd_tree = self.restriction_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/simpleType/restriction')[0]

        result_string = generate_restriction(self.request, xsd_element, xsd_tree, '', full_path='')
        # print result_string

        expected_element = {
            'tag': 'restriction',
            'occurs': (1, 1, 1),
            'value': None,
            'module': None,
            'children': [
                {
                    'tag': 'enumeration',
                    'occurs': (1, 1, 1),
                    'value': 'child0',
                    'module': None,
                    'children': []
                },
                {
                    'tag': 'enumeration',
                    'occurs': (1, 1, 1),
                    'value': 'child1',
                    'module': None,
                    'children': []
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.restriction_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    def test_create_simple_type(self):
        xsd_files = join('simple_type', 'basic')
        xsd_tree = self.restriction_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/simpleType/restriction')[0]

        result_string = generate_restriction(self.request, xsd_element, xsd_tree, '', full_path='')
        # print result_string

        expected_element = {
            'tag': 'restriction',
            'occurs': (1, 1, 1),
            'value': None,
            'module': None,
            'children': [
                {
                    'tag': 'simple_type',
                    'occurs': (1, 1, 1),
                    'value': None,
                    'module': None,
                    'children': [
                        {
                            'tag': 'restriction',
                            'occurs': (1, 1, 1),
                            'value': None,
                            'module': None,
                            'children': [
                                {
                                    'tag': 'enumeration',
                                    'occurs': (1, 1, 1),
                                    'value': 'child0',
                                    'module': None,
                                    'children': []
                                },
                                {
                                    'tag': 'enumeration',
                                    'occurs': (1, 1, 1),
                                    'value': 'child1',
                                    'module': None,
                                    'children': []
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.restriction_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_enumeration(self):
        xsd_files = join('enumeration', 'basic')
        xsd_tree = self.restriction_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/simpleType/restriction')[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.restriction_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_restriction(self.request, xsd_element, xsd_tree, '', full_path='/root',
                                             edit_data_tree=edit_data_tree)
        # print result_string
        # result_string = '<div>' + result_string + '</div>'

        expected_element = {
            'tag': 'restriction',
            'occurs': (1, 1, 1),
            'value': None,
            'module': None,
            'children': [
                {
                    'tag': 'enumeration',
                    'occurs': (1, 1, 1),
                    'value': 'child0',
                    'module': None,
                    'children': []
                },
                {
                    'tag': 'enumeration/selected',
                    'occurs': (1, 1, 1),
                    'value': 'child1',
                    'module': None,
                    'children': []
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.restriction_data_handler.get_html2(xsd_files + '.reload')

        self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_simple_type(self):
        xsd_files = join('simple_type', 'basic')
        xsd_tree = self.restriction_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/simpleType/restriction')[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.restriction_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_restriction(self.request, xsd_element, xsd_tree, '', full_path='/root',
                                             edit_data_tree=edit_data_tree)
        # print result_string
        # result_string = '<div>' + result_string + '</div>'

        expected_element = {
            'tag': 'restriction',
            'occurs': (1, 1, 1),
            'value': None,
            'module': None,
            'children': [
                {
                    'tag': 'simple_type',
                    'occurs': (1, 1, 1),
                    'value': None,
                    'module': None,
                    'children': [
                        {
                            'tag': 'restriction',
                            'occurs': (1, 1, 1),
                            'value': None,
                            'module': None,
                            'children': [
                                {
                                    'tag': 'enumeration/selected',
                                    'occurs': (1, 1, 1),
                                    'value': 'child0',
                                    'module': None,
                                    'children': []
                                },
                                {
                                    'tag': 'enumeration',
                                    'occurs': (1, 1, 1),
                                    'value': 'child1',
                                    'module': None,
                                    'children': []
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_element)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.restriction_data_handler.get_html2(xsd_files + '.reload')

        self.assertTrue(are_equals(result_html, expected_html))


class ParserGenerateExtensionTestSuite(TestCase):
    """
    """
    # FIXME Every test is broken due to the non support of extension by the parser

    def setUp(self):
        extension_data = join('curate', 'tests', 'data', 'parser', 'extension')
        self.extension_data_handler = DataHandler(extension_data)

        self.request = HttpRequest()
        engine = import_module('django.contrib.sessions.backends.db')
        session_key = None
        self.request.session = engine.SessionStore(session_key)

        self.request.session['curate_edit'] = False  # Data edition
        self.request.session['nb_html_tags'] = 0
        self.request.session['mapTagID'] = {}
        self.request.session['nbChoicesID'] = 0
        self.request.session['defaultPrefix'] = 'test'

    def test_create_group(self):
        xsd_files = join('group', 'basic')
        xsd_tree = self.extension_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/element/complexType/complexContent/extension')[0]

        result_string = generate_extension(self.request, xsd_element, xsd_tree, '', full_path='')
        # print result_string

        expected_dict = {
            'tag': 'extension',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'input',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': '',
                    'children': [

                    ]
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_dict)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.extension_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    def test_create_all(self):
        xsd_files = join('all', 'basic')
        xsd_tree = self.extension_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/element/complexType/complexContent/extension')[0]

        result_string = generate_extension(self.request, xsd_element, xsd_tree, '', full_path='')
        # print result_string

        expected_dict = {
            'tag': 'extension',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'input',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': '',
                    'children': [

                    ]
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_dict)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.extension_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    def test_create_choice(self):
        xsd_files = join('choice', 'basic')
        xsd_tree = self.extension_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/element/complexType/complexContent/extension')[0]

        result_string = generate_extension(self.request, xsd_element, xsd_tree, '', full_path='')
        # print result_string

        expected_dict = {
            'tag': 'extension',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'input',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': '',
                    'children': [

                    ]
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_dict)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.extension_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    def test_create_sequence(self):
        xsd_files = join('sequence', 'basic')
        xsd_tree = self.extension_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/element/complexType/complexContent/extension')[0]

        result_string = generate_extension(self.request, xsd_element, xsd_tree, '', full_path='')
        # print result_string

        expected_dict = {
            'tag': 'extension',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'input',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': '',
                    'children': [

                    ]
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_dict)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.extension_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    def test_create_attribute(self):
        xsd_files = join('attribute', 'basic')
        xsd_tree = self.extension_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/element/complexType/simpleContent/extension')[0]

        result_string = generate_extension(self.request, xsd_element, xsd_tree, '', full_path='')
        # print result_string

        expected_dict = {
            'tag': 'extension',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'input',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': '',
                    'children': [

                    ]
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_dict)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.extension_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    def test_create_attribute_group(self):
        xsd_files = join('attribute_group', 'basic')
        xsd_tree = self.extension_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/element/complexType/simpleContent/extension')[0]

        result_string = generate_extension(self.request, xsd_element, xsd_tree, '', full_path='')
        # print result_string

        expected_dict = {
            'tag': 'extension',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'input',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': '',
                    'children': [

                    ]
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_dict)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.extension_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    def test_create_any_attribute(self):
        xsd_files = join('any_attribute', 'basic')
        xsd_tree = self.extension_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/element/complexType/simpleContent/extension')[0]

        result_string = generate_extension(self.request, xsd_element, xsd_tree, '', full_path='')
        # print result_string

        expected_dict = {
            'tag': 'extension',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'input',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': '',
                    'children': [

                    ]
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_dict)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.extension_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    def test_create_multiple(self):
        xsd_files = join('multiple', 'basic')
        xsd_tree = self.extension_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/element/complexType/complexContent/extension')[0]

        result_string = generate_extension(self.request, xsd_element, xsd_tree, '', full_path='')
        # print result_string

        expected_dict = {
            'tag': 'extension',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'input',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': '',
                    'children': [

                    ]
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_dict)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.extension_data_handler.get_html2(xsd_files)

        self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_group(self):
        # fixme display is not correct
        xsd_files = join('group', 'basic')
        xsd_tree = self.extension_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/element/complexType/complexContent/extension')[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.extension_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_extension(self.request, xsd_element, xsd_tree, '', full_path='/test0',
                                           edit_data_tree=edit_data_tree)
        # print result_string
        # result_string = '<div>' + result_string + '</div>'

        expected_dict = {
            'tag': 'extension',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'input',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': '',
                    'children': [

                    ]
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_dict)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.extension_data_handler.get_html2(xsd_files + '.reload')

        self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_all(self):
        # fixme bugs
        xsd_files = join('all', 'basic')
        xsd_tree = self.extension_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/element/complexType/complexContent/extension')[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.extension_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_extension(self.request, xsd_element, xsd_tree, '', full_path='/test1',
                                           edit_data_tree=edit_data_tree)
        # print result_string
        # result_string = '<div>' + result_string + '</div>'

        expected_dict = {
            'tag': 'extension',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'input',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': '',
                    'children': [

                    ]
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_dict)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.extension_data_handler.get_html2(xsd_files + '.reload')

        self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_choice(self):
        xsd_files = join('choice', 'basic')
        xsd_tree = self.extension_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/element/complexType/complexContent/extension')[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.extension_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_extension(self.request, xsd_element, xsd_tree, '', full_path='/test2',
                                           edit_data_tree=edit_data_tree)
        # print result_string
        # result_string = '<div>' + result_string + '</div>'

        expected_dict = {
            'tag': 'extension',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'input',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': '',
                    'children': [

                    ]
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_dict)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.extension_data_handler.get_html2(xsd_files + '.reload')

        self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_sequence(self):
        xsd_files = join('sequence', 'basic')
        xsd_tree = self.extension_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/element/complexType/complexContent/extension')[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.extension_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_extension(self.request, xsd_element, xsd_tree, '', full_path='/test3',
                                           edit_data_tree=edit_data_tree)
        # print result_string
        # result_string = '<div>' + result_string + '</div>'

        expected_dict = {
            'tag': 'extension',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'input',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': '',
                    'children': [

                    ]
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_dict)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.extension_data_handler.get_html2(xsd_files + '.reload')

        self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_attribute(self):
        xsd_files = join('attribute', 'basic')
        xsd_tree = self.extension_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/element/complexType/simpleContent/extension')[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.extension_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_extension(self.request, xsd_element, xsd_tree, '', full_path='/test4',
                                           edit_data_tree=edit_data_tree)
        # print result_string
        # result_string = '<div>' + result_string + '</div>'

        expected_dict = {
            'tag': 'extension',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'input',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': 'entry0',
                    'children': [

                    ]
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_dict)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.extension_data_handler.get_html2(xsd_files + '.reload')

        self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_attribute_group(self):
        xsd_files = join('attribute_group', 'basic')
        xsd_tree = self.extension_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/element/complexType/simpleContent/extension')[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.extension_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_extension(self.request, xsd_element, xsd_tree, '', full_path='/test5',
                                           edit_data_tree=edit_data_tree)
        # print result_string
        # result_string = '<div>' + result_string + '</div>'

        expected_dict = {
            'tag': 'extension',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'input',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': 'entry0',
                    'children': [

                    ]
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_dict)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.extension_data_handler.get_html2(xsd_files + '.reload')

        self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_any_attribute(self):
        xsd_files = join('any_attribute', 'basic')
        xsd_tree = self.extension_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/element/complexType/simpleContent/extension')[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.extension_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_extension(self.request, xsd_element, xsd_tree, '', full_path='/test6',
                                           edit_data_tree=edit_data_tree)
        # print result_string
        # result_string = '<div>' + result_string + '</div>'

        expected_dict = {
            'tag': 'extension',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'input',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': 'entry0',
                    'children': [

                    ]
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_dict)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.extension_data_handler.get_html2(xsd_files + '.reload')

        self.assertTrue(are_equals(result_html, expected_html))

    def test_reload_multiple(self):
        xsd_files = join('multiple', 'basic')
        xsd_tree = self.extension_data_handler.get_xsd2(xsd_files)
        xsd_element = xsd_tree.xpath('/schema/element/complexType/complexContent/extension')[0]

        self.request.session['curate_edit'] = True

        xml_tree = self.extension_data_handler.get_xml(xsd_files)
        xml_data = etree.tostring(xml_tree)

        clean_parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, remove_pis=True)
        etree.set_default_parser(parser=clean_parser)
        # load the XML tree from the text
        edit_data_tree = etree.XML(str(xml_data.encode('utf-8')))
        result_string = generate_extension(self.request, xsd_element, xsd_tree, '', full_path='/test7',
                                           edit_data_tree=edit_data_tree)
        # print result_string
        # result_string = '<div>' + result_string + '</div>'

        expected_dict = {
            'tag': 'extension',
            'occurs': (1, 1, 1),
            'module': None,
            'value': None,
            'children': [
                {
                    'tag': 'input',
                    'occurs': (1, 1, 1),
                    'module': None,
                    'value': '',
                    'children': [

                    ]
                }
            ]
        }

        self.assertDictEqual(result_string[1], expected_dict)

        result_html = etree.fromstring(result_string[0])
        expected_html = self.extension_data_handler.get_html2(xsd_files + '.reload')

        self.assertTrue(are_equals(result_html, expected_html))
