import unittest
from queue import Queue
from coalib.settings.Section import Section
from bears.jinja2.Jinja2Bear import Jinja2Bear
from coalib.testing.LocalBearTestHelper import verify_local_bear, execute_bear


Jinja2BearVariableSpacingTest = verify_local_bear(
    Jinja2Bear,
    valid_files=(r'foo {{ var }}',
                 r'foo {{ var1|filter }} bar {{ var2 }}'),
    invalid_files=(r'foo {{var }}',
                   r'foo {{ var}} bar',
                   r'{{  var }}',
                   r'{{ good_var }} foo {{bad_var }}'))

Jinja2BearCustomVariableSpacingTest = verify_local_bear(
    Jinja2Bear,
    valid_files=(r'foo {{var}}',
                 r'foo {{var1|filter}} bar {{var2}}'),
    invalid_files=(r'foo {{ var }}',
                   r'foo {{ var}} bar',
                   r'{{  var }}'),
    settings={'variable_spacing': '0'})

Jinja2BearStatementSpacingTest = verify_local_bear(
    Jinja2Bear,
    valid_files=(r'foo {% statement1 %} bar',
                 r'foo {% statement2 foobar %} bar',
                 r'foo {%+ statement3 %} bar',
                 r'foo {%+ statement4 -%} bar',
                 r'foo {% statement5 -%} bar',
                 r'foo {%- statement1 +%} bar'),
    invalid_files=(r'foo {%foo bar %} bar',
                   r'foo {% foo bar%} bar',
                   r'foo {%foo bar%} bar',
                   r'foo {%   foo bar  %} bar',
                   r'foo {%+   statement3     %} bar',
                   r'foo {%+statement4    -%} bar',
                   r'foo {%    statement5-%} bar',
                   r'foo {%-  statement1    +%} bar'))

Jinja2BearCustomStatementSpacingTest = verify_local_bear(
    Jinja2Bear,
    valid_files=(r'foo {%statement1%} bar',
                 r'foo {%statement2 foobar%} bar',
                 r'foo {%+statement3%} bar',
                 r'foo {%+statement4-%} bar',
                 r'foo {%statement5-%} bar',
                 r'foo {%-statement1+%} bar'),
    invalid_files=(r'foo {%foo bar %} bar',
                   r'foo {% foo bar%} bar',
                   r'foo {% foo bar %} bar',
                   r'foo {%   foo bar  %} bar',
                   r'foo {%+   statement3     %} bar',
                   r'foo {%+statement4    -%} bar',
                   r'foo {%    statement5-%} bar',
                   r'foo {%-  statement1    +%} bar'),
    settings={'statement_spacing': '0'})


class Jinja2BearSpacingDiffTest(unittest.TestCase):

    def setUp(self):
        self.uut = Jinja2Bear(Section(''), Queue())

    def test_variable_spacing(self):
        content = (r'foo {{var }} bar',)
        with execute_bear(self.uut, 'F', content) as result:
            self.assertEqual(result[0].diffs['F'].unified_diff,
                             '--- \n'
                             '+++ \n'
                             '@@ -1 +1 @@\n'
                             '-foo {{var }} bar\n'
                             '+foo {{ var }} bar')

    def test_statement_spacing(self):
        content = (r'foo {%-statement1 %} bar',)
        with execute_bear(self.uut, 'F', content) as result:
            self.assertEqual(result[0].diffs['F'].unified_diff,
                             '--- \n'
                             '+++ \n'
                             '@@ -1 +1 @@\n'
                             '-foo {%-statement1 %} bar\n'
                             '+foo {%- statement1 %} bar')

    def test_control_spacing(self):
        content = [
            '{% for x in y %}\n',
            'rendering stuff\n',
            '{% endfor%}{# for x in y #}\n'
        ]
        with execute_bear(self.uut, 'F', content) as result:
            self.assertEqual(result[0].diffs['F'].unified_diff,
                             '--- \n'
                             '+++ \n'
                             '@@ -1,3 +1,3 @@\n'
                             ' {% for x in y %}\n'
                             ' rendering stuff\n'
                             '-{% endfor%}{# for x in y #}\n'
                             '+{% endfor %}{# for x in y #}\n')


Jinja2BearControlSpacingTest = verify_local_bear(
    Jinja2Bear,
    valid_files=(r'foo {% if something %} bar {% endif %}',
                 r'foo {%+ if something -%} bar {%+ endif -%}',
                 r'foo {%- if something +%} bar {%- endif +%}',
                 r'foo {%+ for x in y +%} foobar {%- endfor -%}'),
    invalid_files=(r'foo {% if var%} bar {% endif %}',
                   r'{% if something %} foo {%endif%}{# if something #}',
                   r'foo {%+if something    -%} bar {%+endif-%}',
                   r'foo {%-   if something+%} bar {%-   endif    +%}',
                   r'{%for a in var %} {% endfor %}',
                   r'foo {%+for x in y+%} foobar {%-    endfor   -%}'))

Jinja2BearCustomControlSpacingTest = verify_local_bear(
    Jinja2Bear,
    valid_files=(r'foo {%if something%} bar {%endif%}',
                 r'foo {%+if something-%} bar {%+endif-%}',
                 r'foo {%-if something+%} bar {%-endif+%}',
                 r'foo {%+for x in y+%} foobar {%-endfor-%}'),
    invalid_files=(r'foo {% if var%} bar {%endif%}',
                   r'foo {%if foo%} bar {% endif%}',
                   r'foo {%+ if something -%} bar {%+  endif -%}',
                   r'foo {%-   if something +%} bar {%-   endif    +%}',
                   r'{%for a in var %} {%endfor%}',
                   r'foo {%+ for x in y +%} foobar {%-    endfor   -%}'),
    settings={'control_spacing': '0'})


good_file1 = """
foo
{% for x in something %}
render stuff
{% endfor %}{# for x in something #}
"""

good_file2 = """
foo
{%+ if x == something -%}
render stuff
{%- endif +%}{# if x == something #}
"""

good_file3 = '{%+ for x in y +%} one liner needs no label {%- endfor -%}'

bad_file1 = """
foo
{% for x in something %}
render stuff
{% endfor %} more stuff
"""

bad_file2 = """
foo
{%+ if x == something -%}
render stuff
{%- endif +%}{# some random comment #} more stuff
"""

Jinja2BearForLoopLabelTest = verify_local_bear(
    Jinja2Bear,
    valid_files=(good_file1, good_file2, good_file3),
    invalid_files=(bad_file1, bad_file2))

valid_file_without_end_comments = """
foo
{% for x in something %}
render stuff
{% endfor %}
"""

valid_file_with_end_comments = """
foo
{% for x in something %}
render stuff
{% endfor %}{# for x in something #}
"""

Jinja2BearForLoopLabelDisableTest = verify_local_bear(
    Jinja2Bear,
    valid_files=(valid_file_without_end_comments,
                 valid_file_with_end_comments),
    invalid_files=(),
    settings={'check_end_labels': 'False'})


class Jinja2BearLabelDiffTest(unittest.TestCase):

    def setUp(self):
        self.section = Section('')
        self.uut = Jinja2Bear(self.section, Queue())

    def test_missing_label(self):
        content = [line + '\n' for line in bad_file1.splitlines()]
        with execute_bear(self.uut, 'F', content) as result:
            self.assertEqual(
                result[0].diffs['F'].unified_diff,
                '--- \n'
                '+++ \n'
                '@@ -2,4 +2,4 @@\n'
                ' foo\n'
                ' {% for x in something %}\n'
                ' render stuff\n'
                '-{% endfor %} more stuff\n'
                '+{% endfor %}{# for x in something #} more stuff\n')

    def test_wrong_label(self):
        content = [line + '\n' for line in bad_file2.splitlines()]
        with execute_bear(self.uut, 'F', content) as result:
            self.assertEqual(
                result[0].diffs['F'].unified_diff,
                '--- \n'
                '+++ \n'
                '@@ -2,4 +2,4 @@\n'
                ' foo\n'
                ' {%+ if x == something -%}\n'
                ' render stuff\n'
                '-{%- endif +%}{# some random comment #} more stuff\n'
                '+{%- endif +%}{# if x == something #} more stuff\n')


Jinja2BearControlBlockTest = verify_local_bear(
    Jinja2Bear,
    valid_files=('foo {% for a in b %} bar {% endfor %}',),
    invalid_files=('This {% for a in b %} has no closing tag',
                   'This {% endif %} has no open tag'))

good_indent_file1 = """
{% for tony in avengers %}
  {% for thanos in enemy %}
render stuff
  {% endfor %}{# for thanos in enemy #}
{% endfor %}{# for tony in avengers #}
"""

good_indent_file2 = """
import some_stuff
for x in y:
{% if x is True %}
print("This line doesn't get affected by indentatoin")
{% elif %}
print("Bye Bye")
{% endif %}{# if x is True #}

{% if x in y %}
some statement
{% endif %}{# if x in y #}
"""

good_indent_file3 = """
{% if x in y %}
  {% for var in variable %}
    {% set var1 in y %}
  {% endfor %}{# for var in variable #}
{% endif %}{# if x in y #}
"""

good_indent_file4 = """
{% for x in y %}
  {% if y in z %}
    {% set var1 = value1 %}
  {% elif %}
    {% set var2 = value2 %}
  {% else %}
    {% set var3 = value3 %}
  {% endif %}{# if y in z #}
{% endfor %}{# for x in y #}

{% if y in z %}
{% elif %}
  {% set var4 = value4 %}
{% else %}
{% endif %}{# if y in z #}
"""

bad_indent_file1 = """
{% for tony in avengers %}
{% for thanos in enemy %}
render stuff
  {% endfor %}
{% endfor %}
"""

bad_indent_file2 = """
import some_stuff
for x in y:
  {% if x is True %}
  print("This line doesn't get affected by indentatoin")
     {% elif %}
  print("Bye Bye")
  {% endif %}

"""
bad_indent_file3 = """
{% if x in y %}
  {% for var in variable %}
  {% set var1 in y %}
{% endfor %}{# for var in variable #}
{% endif %}{# if x in y #}
"""

bad_indent_file4 = """
{% if x in y %}
some statement
  {% endif %}{# if x in y #}
"""

bad_indent_file5 = """
{% for var in variable %}
{% set var1 in y %}
{% endfor %}{# for var in variable #}
"""

valid_file_with_no_indentation = """
{% for tony in avengers %}
{% for thanos in enemy %}
render stuff
{% endfor %}{# for thanos in enemy #}
{% endfor %}{# for tony in avengers #}
"""
valid_file_with_bad_indentation = """
{% if x in y %}
{% for var in variable %}
    {% set var1 in y %}
  {% endfor %}{# for var in variable #}
{% endif %}{# if x in y #}
"""
Jinja2BearIndentationDisableTest = verify_local_bear(
    Jinja2Bear,
    valid_files=(valid_file_with_no_indentation,
                 valid_file_with_bad_indentation),
    invalid_files=(),
    settings={'check_indentation': 'False'})

Jinja2BearIndentationEnableTest = verify_local_bear(
    Jinja2Bear,
    valid_files=(good_indent_file1, good_indent_file2, good_indent_file3,
                 good_indent_file4),
    invalid_files=(bad_indent_file1, bad_indent_file2, bad_indent_file3,
                   bad_indent_file4, bad_indent_file5),
    settings={'check_indentation': 'True'})


class Jinja2BearIndentationDiffTest(unittest.TestCase):

    def setUp(self):
        self.section = ''
        self.section.append(Setting('check_indentation', 'True'))
        self.uut = Jinja2Bear(self.section, Queue())

        def test_bad_indentation(self):
            content = [line + '\n' for line in bad_indent_file4.splitlines()]
            with execute_bear(self.uut, 'F', content) as result:
                self.assertEqual(
                    result[0].diffs['F'].unified_diff,
                    '--- \n'
                    '+++ \n'
                    '{% if x in y %}\n'
                    'some statement\n'
                    '-  {% endif %}{# if x in y #}\n'
                    '+{% endif %}{# if x in y #}\n')
