import os
import unittest

from file_generator import FileGenerator
from parser.cxxd_config_parser import CxxdConfigParser

class ClangTidyTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.file_to_perform_clang_tidy_on = FileGenerator.gen_simple_cpp_file()
        cls.project_root_directory        = os.path.dirname(cls.file_to_perform_clang_tidy_on.name)
        cls.txt_compilation_database      = FileGenerator.gen_txt_compilation_database()
        cls.json_compilation_database     = FileGenerator.gen_json_compilation_database(cls.file_to_perform_clang_tidy_on.name)
        cls.target                        = 'debug'
        cls.cxxd_config_with_json_comp_db = FileGenerator.gen_cxxd_config_filename(cls.target, os.path.dirname(cls.json_compilation_database.name))

    @classmethod
    def tearDownClass(cls):
        FileGenerator.close_gen_file(cls.file_to_perform_clang_tidy_on)
        FileGenerator.close_gen_file(cls.json_compilation_database)
        FileGenerator.close_gen_file(cls.txt_compilation_database)
        FileGenerator.close_gen_file(cls.cxxd_config_with_json_comp_db)

    def setUp(self):
        import cxxd_mocks
        from services.clang_tidy_service import ClangTidy
        self.service = ClangTidy(self.project_root_directory, CxxdConfigParser(self.cxxd_config_with_json_comp_db.name, self.project_root_directory), self.target, cxxd_mocks.ServicePluginMock())

    def test_if_compile_flags_are_not_none(self):
        self.assertNotEqual(self.service.clang_tidy_compile_flags, None)

    def test_if_clang_tidy_binary_is_available_on_the_system_path(self):
        self.assertNotEqual(self.service.clang_tidy_binary, None)

    def test_if_startup_callback_sets_compile_flags_accordingly_when_json_compilation_database_provided(self):
        self.assertEqual(self.service.clang_tidy_compile_flags, '-p ' + self.json_compilation_database.name)

    #def test_if_startup_callback_sets_compile_flags_accordingly_when_txt_compilation_database_provided(self):
    #    import cxxd_mocks
    #    from services.clang_tidy_service import ClangTidy
    #    cxxd_config_with_simple_txt = FileGenerator.gen_cxxd_config_filename(self.target, os.path.dirname(self.txt_compilation_database.name), 'compile-flags')
    #    service_with_simple_txt = ClangTidy(self.project_root_directory, CxxdConfigParser(cxxd_config_with_simple_txt.name, self.project_root_directory), self.target, cxxd_mocks.ServicePluginMock())
    #    with open(self.txt_compilation_database.name, 'r') as fd_compile_flags:
    #        compile_flags = [flag.strip() for flag in fd_compile_flags.readlines()]
    #        self.assertEqual(service_with_simple_txt.clang_tidy_compile_flags, '-- ' + ' '.join(compile_flags))
    #    FileGenerator.close_gen_file(cxxd_config_with_simple_txt)

    def test_if_startup_callback_sets_compile_flags_accordingly_with_auto_discovery_mode_even_when_unsupported_compilation_database_provided(self):
        import cxxd_mocks
        from services.clang_tidy_service import ClangTidy
        service_with_unsupported_conf = ClangTidy(self.project_root_directory, CxxdConfigParser('unsupported_config_format.yaml', self.project_root_directory), self.target, cxxd_mocks.ServicePluginMock())
        self.assertNotEqual(service_with_unsupported_conf.clang_tidy_compile_flags, None)

    #def test_if_startup_callback_sets_compile_flags_accordingly_when_compilation_database_file_provided_is_not_existing(self):
    #    self.assertEqual(self.service.clang_tidy_compile_flags, None)
    #    self.service.startup_callback(['some_totally_compilation_database_random_name'])
    #    self.assertEqual(self.service.clang_tidy_compile_flags, None)

    #def test_if_startup_callback_sets_compile_flags_accordingly_when_clang_tidy_binary_is_not_available_on_the_system_path(self):
    #    self.service.clang_tidy_binary = None
    #    self.assertEqual(self.service.clang_tidy_compile_flags, None)
    #    self.service.startup_callback([self.json_compilation_database.name])
    #    self.assertEqual(self.service.clang_tidy_compile_flags, None)

    def test_if_call_returns_true_for_success_and_file_containing_clang_tidy_output_when_run_on_existing_file_without_applying_fixes(self):
        success, clang_tidy_output = self.service([self.file_to_perform_clang_tidy_on.name, False])
        self.assertEqual(success, True)
        self.assertNotEqual(clang_tidy_output, None)

    def test_if_call_returns_true_for_success_and_file_containing_clang_tidy_output_when_run_on_existing_file_with_applying_fixes(self):
        success, clang_tidy_output = self.service([self.file_to_perform_clang_tidy_on.name, True])
        self.assertEqual(success, True)
        self.assertNotEqual(clang_tidy_output, None)

    def test_if_call_returns_false_for_success_and_no_output_when_run_on_inexisting_file_without_applying_fixes(self):
        success, clang_tidy_output = self.service(['inexisting_filename', False])        
        self.assertEqual(success, False)
        self.assertEqual(clang_tidy_output, None)

    def test_if_call_returns_false_for_success_and_no_output_when_run_on_inexisting_file_with_applying_fixes(self):
        success, clang_tidy_output = self.service(['inexisting_filename', True])        
        self.assertEqual(success, False)
        self.assertEqual(clang_tidy_output, None)

    def test_if_call_returns_false_for_success_and_no_output_when_clang_tidy_binary_is_not_available_on_the_system_path(self):
        self.service.clang_tidy_binary = None
        success, clang_tidy_output = self.service([self.file_to_perform_clang_tidy_on.name, False])        
        self.assertEqual(success, False)
        self.assertEqual(clang_tidy_output, None)

    def test_if_call_returns_false_for_success_and_no_output_when_compile_flags_are_not_available(self):
        self.service.clang_tidy_compile_flags = None
        success, clang_tidy_output = self.service([self.file_to_perform_clang_tidy_on.name, False])        
        self.assertEqual(success, False)
        self.assertEqual(clang_tidy_output, None)

class ClangTidyWithTxtConfigTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.file_to_perform_clang_tidy_on = FileGenerator.gen_simple_cpp_file()
        cls.project_root_directory        = os.path.dirname(cls.file_to_perform_clang_tidy_on.name)
        cls.txt_compilation_database      = FileGenerator.gen_txt_compilation_database()
        cls.target                        = 'debug'
        cls.cxxd_config_with_simple_txt   = FileGenerator.gen_cxxd_config_filename(cls.target, os.path.dirname(cls.txt_compilation_database.name), 'compile-flags')

    @classmethod
    def tearDownClass(cls):
        FileGenerator.close_gen_file(cls.file_to_perform_clang_tidy_on)
        FileGenerator.close_gen_file(cls.txt_compilation_database)
        FileGenerator.close_gen_file(cls.cxxd_config_with_simple_txt)

    def setUp(self):
        import cxxd_mocks
        from services.clang_tidy_service import ClangTidy
        self.service = ClangTidy(self.project_root_directory, CxxdConfigParser(self.cxxd_config_with_simple_txt.name, self.project_root_directory), self.target, cxxd_mocks.ServicePluginMock())

    def test_if_startup_callback_sets_compile_flags_accordingly_when_txt_compilation_database_provided(self):
        with open(self.txt_compilation_database.name, 'r') as fd_compile_flags:
            compile_flags = [flag.strip() for flag in fd_compile_flags.readlines()]
            self.assertEqual(self.service.clang_tidy_compile_flags, '-- ' + ' '.join(compile_flags))

if __name__ == '__main__':
    unittest.main()

