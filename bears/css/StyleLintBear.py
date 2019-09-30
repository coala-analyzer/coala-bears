import json

from coalib.bearlib.abstractions.Linter import linter
from dependency_management.requirements.NpmRequirement import NpmRequirement


@linter(executable='stylelint',
        output_format='regex',
        output_regex=r'\s*(?P<filename>.+)\s*(?P<line>\d+):(?P<column>\d+)\s*'
                     r'\D\s*(?P<message>.+)',
        config_suffix='.json',
        use_stdout=True,
        use_stderr=False)
class StyleLintBear:
    """
    Checks the code with stylelint. This will run stylelint over each file
    separately.

    Detect errors and potential problems in CSS code and to enforce
    appropriate coding conventions. For example, problems like syntax errors,
    invalid color codes etc can be detected.

    For more information on the analysis visit <http://stylelint.io/>
    """
    LANGUAGES = {'CSS', 'SCSS'}
    REQUIREMENTS = {NpmRequirement('stylelint', '10.0.1')}
    AUTHORS = {'The coala developers'}
    AUTHORS_EMAILS = {'coala-devel@googlegroups.com'}
    LICENSE = 'AGPL-3.0'
    CAN_DETECT = {'Syntax', 'Unused Code', 'Formatting'}

    @staticmethod
    def generate_config(
        filename, file,
        at_rule_empty_line_before: str = None,
        at_rule_name_case: str = 'lower',
        at_rule_name_space_after: str = 'always-single-line',
        at_rule_semicolon_newline_after: str = 'always',
        block_closing_brace_empty_line_before: str = 'never',
        block_closing_brace_newline_after: str = 'always',
        block_closing_brace_newline_before: str = 'always-multi-line',
        block_closing_brace_space_before: str = 'always-single-line',
        block_no_empty: bool = True,
        block_opening_brace_newline_after: str = 'always-multi-line',
        block_opening_brace_space_after: str = 'always-single-line',
        block_opening_brace_space_before: str = 'always',
        color_hex_case: str = 'lower',
        color_hex_length: str = 'short',
        color_no_invalid_hex: bool = True,
        comment_empty_line_before: str = None,
        comment_no_empty: bool = True,
        comment_whitespace_inside: str = 'always',
        custom_property_empty_line_before: str = None,
        declaration_bang_space_after: str = 'never',
        declaration_bang_space_before: str = 'always',
        declaration_block_no_duplicate_properties: bool = None,
        declaration_block_no_redundant_longhand_properties: bool = True,
        declaration_block_no_shorthand_property_overrides: bool = True,
        declaration_block_semicolon_newline_after: str = 'always-multi-line',
        declaration_block_semicolon_space_after: str = 'always-single-line',
        declaration_block_semicolon_space_before: str = 'never',
        declaration_block_single_line_max_declarations: int = 1,
        declaration_block_trailing_semicolon: str = 'always',
        declaration_colon_newline_after: str = 'always-multi-line',
        declaration_colon_space_after: str = 'always-single-line',
        declaration_colon_space_before: str = 'never',
        declaration_empty_line_before: str = None,
        font_family_no_duplicate_names: bool = True,
        function_calc_no_unspaced_operator: bool = True,
        function_comma_newline_after: str = 'always-multi-line',
        function_comma_space_after: str = 'always-single-line',
        function_comma_space_before: str = 'never',
        function_linear_gradient_no_nonstandard_direction: bool = True,
        function_max_empty_lines: int = 0,
        function_name_case: str = 'lower',
        function_parentheses_newline_inside: str = 'always-multi-line',
        function_parentheses_space_inside: str = 'never-single-line',
        function_whitespace_after: str = 'always',
        indentation: int = 2,
        keyframe_declaration_no_important: bool = True,
        length_zero_no_unit: bool = True,
        max_empty_lines: int = 1,
        media_feature_colon_space_after: str = 'always',
        media_feature_colon_space_before: str = 'never',
        media_feature_name_case: str = 'lower',
        media_feature_name_no_unknown: bool = True,
        media_feature_parentheses_space_inside: str = 'never',
        media_feature_range_operator_space_after: str = 'always',
        media_feature_range_operator_space_before: str = 'always',
        media_query_list_comma_newline_after: str = 'always-multi-line',
        media_query_list_comma_space_after: str = 'always-single-line',
        media_query_list_comma_space_before: str = 'never',
        no_empty_source: bool = True,
        no_eol_whitespace: bool = True,
        no_extra_semicolons: bool = True,
        no_invalid_double_slash_comments: bool = True,
        no_missing_end_of_source_newline: bool = True,
        number_leading_zero: str = 'always',
        number_no_trailing_zeros: bool = True,
        property_case: str = 'lower',
        property_no_unknown: bool = True,
        rule_empty_line_before: str = None,
        selector_attribute_brackets_space_inside: str = 'never',
        selector_attribute_operator_space_after: str = 'never',
        selector_attribute_operator_space_before: str = 'never',
        selector_combinator_space_after: str = 'always',
        selector_combinator_space_before: str = 'always',
        selector_descendant_combinator_no_non_space: bool = True,
        selector_list_comma_newline_after: str = 'always',
        selector_list_comma_space_before: str = 'never',
        selector_max_empty_lines: int = 0,
        selector_pseudo_class_case: str = 'lower',
        selector_pseudo_class_no_unknown: bool = True,
        selector_pseudo_class_parentheses_space_inside: str = 'never',
        selector_pseudo_element_case: str = 'lower',
        selector_pseudo_element_colon_notation: str = 'double',
        selector_pseudo_element_no_unknown: bool = True,
        selector_type_case: str = 'lower',
        selector_type_no_unknown: bool = True,
        shorthand_property_no_redundant_values: bool = True,
        string_no_newline: bool = True,
        unit_case: str = 'lower',
        unit_no_unknown: bool = True,
        value_list_comma_newline_after: str = 'always-multi-line',
        value_list_comma_space_after: str = 'always-single-line',
        value_list_comma_space_before: str = 'never',
        value_list_max_empty_lines: int = 0,
    ):
        """
        :param at_rule_empty_line_before:
            Require or disallow an empty line before at-rules (Autofixable).
        :param at_rule_name_case:
            Specify lowercase or uppercase for at-rules names (Autofixable).
        :param at_rule_name_space_after:
            Require a single space after at-rule names (Autofixable).
        :param at_rule_semicolon_newline_after:
            Require a newline after the semicolon of at-rules (Autofixable).
        :param block_closing_brace_empty_line_before:
            Require or disallow an empty line before the closing brace of
            blocks (Autofixable).
        :param block_closing_brace_newline_after:
            Require a newline or disallow whitespace after the closing brace of
            blocks (Autofixable).
        :param block_closing_brace_newline_before:
            Require a newline or disallow whitespace before the closing brace
            of blocks (Autofixable).
        :param block_closing_brace_space_before:
            Require a single space or disallow whitespace before the closing
            brace of blocks (Autofixable).
        :param block_no_empty:
            Disallow empty blocks.
        :param block_opening_brace_newline_after:
            Require a newline after the opening brace of blocks (Autofixable).
        :param block_opening_brace_space_after:
            Require a single space or disallow whitespace after the opening
            brace of blocks (Autofixable).
        :param block_opening_brace_space_before:
            Require a single space or disallow whitespace before the opening
            brace of blocks (Autofixable).
        :param color_hex_case:
            Specify lowercase or uppercase for hex colors (Autofixable).
        :param color_hex_length:
            Specify short or long notation for hex colors (Autofixable).
        :param color_no_invalid_hex:
            Disallow invalid hex colors.
        :param comment_empty_line_before:
            Require or disallow an empty line before comments (Autofixable).
        :param comment_no_empty:
            Disallow empty comments.
        :param comment_whitespace_inside:
            Require or disallow whitespace on the inside of comment markers
            (Autofixable).
        :param custom_property_empty_line_before:
            Require or disallow an empty line before custom properties
            (Autofixable).
        :param declaration_bang_space_after:
            Require a single space or disallow whitespace after the bang of
            declarations (Autofixable).
        :param declaration_bang_space_before:
            Require a single space or disallow whitespace before the bang of
            declarations (Autofixable).
        :param declaration_block_no_duplicate_properties:
            Disallow duplicate properties within declaration blocks.
        :param declaration_block_no_redundant_longhand_properties:
            Disallow longhand properties that can be combined into one
            shorthand property.
        :param declaration_block_no_shorthand_property_overrides:
            Disallow shorthand properties that override related longhand
            properties within declaration blocks.
        :param declaration_block_semicolon_newline_after:
            Require a newline or disallow whitespace after the semicolons of
            declaration blocks (Autofixable).
        :param declaration_block_semicolon_space_after:
            Require a single space or disallow whitespace after the semicolons
            of declaration blocks.
        :param declaration_block_semicolon_space_before:
            Require a single space or disallow whitespace before the semicolons
            of declaration blocks (Autofixable).
        :param declaration_block_single_line_max_declarations:
            Limit the number of declarations within single line declaration
            blocks.
        :param declaration_block_trailing_semicolon:
            Require or disallow a trailing semicolon within declaration blocks
            (Autofixable).
        :param declaration_colon_newline_after:
            Require a newline or disallow whitespace after the colon of
            declarations (Autofixable).
        :param declaration_colon_space_after:
            Require a single space or disallow whitespace after the colon of
            declarations (Autofixable).
        :param declaration_colon_space_before:
            Require a single space or disallow whitespace before the colon of
            declarations (Autofixable).
        :param declaration_empty_line_before:
            Require or disallow an empty line before declarations
            (Autofixable).
        :param font_family_no_duplicate_names:
            Disallow duplicate font family names.
        :param function_calc_no_unspaced_operator:
            Disallow an unspaced operator within calc functions.
        :param function_comma_newline_after:
            Require a newline or disallow whitespace after the commas of
            functions.
        :param function_comma_space_after:
            Require a single space or disallow whitespace after the commas of
            functions (Autofixable).
        :param function_comma_space_before:
            Require a single space or disallow whitespace before the commas of
            functions (Autofixable).
        :param function_linear_gradient_no_nonstandard_direction:
            Disallow direction values in linear-gradient() calls that are not
            valid according to the standard syntax.
        :param function_max_empty_lines:
            Limit the number of adjacent empty lines within functions
            (Autofixable).
        :param function_name_case:
            Specify lowercase or uppercase for function names (Autofixable).
        :param function_parentheses_newline_inside:
            Require a newline or disallow whitespace on the inside of the
            parentheses of functions (Autofixable).
        :param function_parentheses_space_inside:
            Require a single space or disallow whitespace on the inside of the
            parentheses of functions (Autofixable).
        :param function_whitespace_after:
            Require or disallow whitespace after functions (Autofixable).
        :param indentation:
            Specify indentation (Autofixable).
        :param keyframe_declaration_no_important:
            Disallow !important within keyframe declarations.
        :param length_zero_no_unit:
            Disallow units for zero lengths (Autofixable).
        :param max_empty_lines:
            Limit the number of adjacent empty lines.
        :param media_feature_colon_space_after:
            Require a single space or disallow whitespace after the colon in
            media features (Autofixable).
        :param media_feature_colon_space_before:
            Require a single space or disallow whitespace before the colon in
            media features (Autofixable).
        :param media_feature_name_case:
            Specify lowercase or uppercase for media feature names
            (Autofixable).
        :param media_feature_name_no_unknown:
            Disallow unknown media feature names.
        :param media_feature_parentheses_space_inside:
            Require a single space or disallow whitespace on the inside of the
            parentheses within media features (Autofixable).
        :param media_feature_range_operator_space_after:
            Require a single space or disallow whitespace after the range
            operator in media features (Autofixable).
        :param media_feature_range_operator_space_before:
            Require a single space or disallow whitespace before the range
            operator in media features (Autofixable).
        :param media_query_list_comma_newline_after:
            Require a newline or disallow whitespace after the commas of media
            query lists (Autofixable).
        :param media_query_list_comma_space_after:
            Require a single space or disallow whitespace after the commas of
            media query lists (Autofixable).
        :param media_query_list_comma_space_before:
            Require a single space or disallow whitespace before the commas of
            media query lists (Autofixable).
        :param no_empty_source:
            Disallow empty sources.
        :param no_eol_whitespace:
            Disallow end-of-line whitespace (Autofixable).
        :param no_extra_semicolons:
            Disallow extra semicolons (Autofixable).
        :param no_invalid_double_slash_comments:
            Disallow double-slash comments (//...) which are not supported by
            CSS.
        :param no_missing_end_of_source_newline:
            Disallow missing end-of-source newlines (Autofixable).
        :param number_leading_zero:
            Require or disallow a leading zero for fractional numbers less than
            1 (Autofixable).
        :param number_no_trailing_zeros:
            Disallow trailing zeros in numbers (Autofixable).
        :param property_case:
            Specify lowercase or uppercase for properties (Autofixable).
        :param property_no_unknown:
            Disallow unknown properties.
        :param rule_empty_line_before:
            Require or disallow an empty line before rules (Autofixable).
        :param selector_attribute_brackets_space_inside:
            Require a single space or disallow whitespace on the inside of the
            brackets within attribute selectors (Autofixable).
        :param selector_attribute_operator_space_after:
            Require a single space or disallow whitespace after operators
            within attribute selectors (Autofixable).
        :param selector_attribute_operator_space_before:
            Require a single space or disallow whitespace before operators
            within attribute selectors (Autofixable).
        :param selector_combinator_space_after:
            Require a single space or disallow whitespace after the combinators
            of selectors (Autofixable).
        :param selector_combinator_space_before:
            Require a single space or disallow whitespace before the
            combinators of selectors (Autofixable).
        :param selector_descendant_combinator_no_non_space:
            Disallow non-space characters for descendant combinators of
            selectors (Autofixable).
        :param selector_list_comma_newline_after:
            Require a newline or disallow whitespace after the commas of
            selector lists (Autofixable).
        :param selector_list_comma_space_before:
            Require a single space or disallow whitespace before the commas of
            selector lists (Autofixable).
        :param selector_max_empty_lines:
            Limit the number of adjacent empty lines within selectors.
        :param selector_pseudo_class_case:
            Specify lowercase or uppercase for pseudo-class selectors
            (Autofixable).
        :param selector_pseudo_class_no_unknown:
            Disallow unknown pseudo-class selectors.
        :param selector_pseudo_class_parentheses_space_inside:
            Require a single space or disallow whitespace on the inside of the
            parentheses within pseudo-class selectors (Autofixable).
        :param selector_pseudo_element_case:
            Specify lowercase or uppercase for pseudo-element selectors.
        :param selector_pseudo_element_colon_notation:
            Specify single or double colon notation for applicable
            pseudo-elements (Autofixable).
        :param selector_pseudo_element_no_unknown:
            Disallow unknown pseudo-element selectors.
        :param selector_type_case:
            Specify lowercase or uppercase for type selector (Autofixable).
        :param selector_type_no_unknown:
            Disallow unknown type selectors.
        :param shorthand_property_no_redundant_values:
            Disallow redundant values in shorthand properties (Autofixable).
        :param string_no_newline:
            Disallow (unescaped) newlines in strings.
        :param unit_case:
            Specify lowercase or uppercase for units (Autofixable).
        :param unit_no_unknown:
            Disallow unknown units.
        :param value_list_comma_newline_after:
            Require a newline or disallow whitespace after the commas of value
            lists (Autofixable).
        :param value_list_comma_space_after:
            Require a single space or disallow whitespace after the commas of
            value lists (Autofixable).
        :param value_list_comma_space_before:
            Require a single space or disallow whitespace before the commas of
            value lists (Autofixable).
        :param value_list_max_empty_lines:
            Limit the number of adjacent empty lines within value lists
            (Autofixable).
        """

        rules = {
            'at-rule-name-case': at_rule_name_case,
            'at-rule-empty-line-before': at_rule_empty_line_before,
            'at-rule-name-space-after': at_rule_name_space_after,
            'at-rule-semicolon-newline-after': (
                at_rule_semicolon_newline_after),
            'block-closing-brace-empty-line-before': (
                block_closing_brace_empty_line_before),
            'block-closing-brace-newline-after': (
                block_closing_brace_newline_after),
            'block-closing-brace-newline-before': (
                block_closing_brace_newline_before),
            'block-closing-brace-space-before': (
                block_closing_brace_space_before),
            'block-no-empty': block_no_empty,
            'block-opening-brace-newline-after': (
                block_opening_brace_newline_after),
            'block-opening-brace-space-after': (
                block_opening_brace_space_after),
            'block-opening-brace-space-before': (
                block_opening_brace_space_before),
            'color-hex-case': color_hex_case,
            'color-hex-length': color_hex_length,
            'color-no-invalid-hex': color_no_invalid_hex,
            'comment-empty-line-before': comment_empty_line_before,
            'comment-no-empty': comment_no_empty,
            'comment-whitespace-inside': comment_whitespace_inside,
            'custom-property-empty-line-before': (
                custom_property_empty_line_before),
            'declaration-bang-space-after': declaration_bang_space_after,
            'declaration-bang-space-before': declaration_bang_space_before,
            'declaration-block-no-duplicate-properties': (
                declaration_block_no_duplicate_properties),
            'declaration-block-no-redundant-longhand-properties': (
                declaration_block_no_redundant_longhand_properties),
            'declaration-block-no-shorthand-property-overrides': (
                declaration_block_no_shorthand_property_overrides),
            'declaration-block-semicolon-newline-after': (
                declaration_block_semicolon_newline_after),
            'declaration-block-semicolon-space-after': (
                declaration_block_semicolon_space_after),
            'declaration-block-semicolon-space-before': (
                declaration_block_semicolon_space_before),
            'declaration-block-single-line-max-declarations': (
                declaration_block_single_line_max_declarations),
            'declaration-block-trailing-semicolon': (
                declaration_block_trailing_semicolon),
            'declaration-colon-newline-after': (
                declaration_colon_newline_after),
            'declaration-colon-space-after': declaration_colon_space_after,
            'declaration-colon-space-before': declaration_colon_space_before,
            'declaration-empty-line-before': declaration_empty_line_before,
            'font-family-no-duplicate-names': font_family_no_duplicate_names,
            'function-calc-no-unspaced-operator': (
                function_calc_no_unspaced_operator),
            'function-comma-newline-after': function_comma_newline_after,
            'function-comma-space-after': function_comma_space_after,
            'function-comma-space-before': function_comma_space_before,
            'function-linear-gradient-no-nonstandard-direction': (
                function_linear_gradient_no_nonstandard_direction),
            'function-max-empty-lines': function_max_empty_lines,
            'function-name-case': function_name_case,
            'function-parentheses-newline-inside': (
                function_parentheses_newline_inside),
            'function-parentheses-space-inside': (
                function_parentheses_space_inside),
            'function-whitespace-after': function_whitespace_after,
            'indentation': indentation,
            'keyframe-declaration-no-important': (
                keyframe_declaration_no_important),
            'length-zero-no-unit': length_zero_no_unit,
            'max-empty-lines': max_empty_lines,
            'media-feature-colon-space-after': (
                media_feature_colon_space_after),
            'media-feature-colon-space-before': (
                media_feature_colon_space_before),
            'media-feature-name-case': media_feature_name_case,
            'media-feature-name-no-unknown': media_feature_name_no_unknown,
            'media-feature-parentheses-space-inside': (
                media_feature_parentheses_space_inside),
            'media-feature-range-operator-space-after': (
                media_feature_range_operator_space_after),
            'media-feature-range-operator-space-before': (
                media_feature_range_operator_space_before),
            'media-query-list-comma-newline-after': (
                media_query_list_comma_newline_after),
            'media-query-list-comma-space-after': (
                media_query_list_comma_space_after),
            'media-query-list-comma-space-before': (
                media_query_list_comma_space_before),
            'no-empty-source': no_empty_source,
            'no-eol-whitespace': no_eol_whitespace,
            'no-extra-semicolons': no_extra_semicolons,
            'no-invalid-double-slash-comments': (
                no_invalid_double_slash_comments),
            'no-missing-end-of-source-newline': (
                no_missing_end_of_source_newline),
            'number-leading-zero': number_leading_zero,
            'number-no-trailing-zeros': number_no_trailing_zeros,
            'property-case': property_case,
            'property-no-unknown': property_no_unknown,
            'rule-empty-line-before': rule_empty_line_before,
            'selector-attribute-brackets-space-inside': (
                selector_attribute_brackets_space_inside),
            'selector-attribute-operator-space-after': (
                selector_attribute_operator_space_after),
            'selector-attribute-operator-space-before': (
                selector_attribute_operator_space_before),
            'selector-combinator-space-after': (
                selector_combinator_space_after),
            'selector-combinator-space-before': (
                selector_combinator_space_before),
            'selector-descendant-combinator-no-non-space': (
                selector_descendant_combinator_no_non_space),
            'selector-list-comma-newline-after': (
                selector_list_comma_newline_after),
            'selector-list-comma-space-before': (
                selector_list_comma_space_before),
            'selector-max-empty-lines': selector_max_empty_lines,
            'selector-pseudo-class-case': selector_pseudo_class_case,
            'selector-pseudo-class-no-unknown': (
                selector_pseudo_class_no_unknown),
            'selector-pseudo-class-parentheses-space-inside': (
                selector_pseudo_class_parentheses_space_inside),
            'selector-pseudo-element-case': selector_pseudo_element_case,
            'selector-pseudo-element-colon-notation': (
                selector_pseudo_element_colon_notation),
            'selector-pseudo-element-no-unknown': (
                selector_pseudo_element_no_unknown),
            'selector-type-case': selector_type_case,
            'selector-type-no-unknown': selector_type_no_unknown,
            'shorthand-property-no-redundant-values': (
                shorthand_property_no_redundant_values),
            'string-no-newline': string_no_newline,
            'unit-case': unit_case,
            'unit-no-unknown': unit_no_unknown,
            'value-list-comma-newline-after': value_list_comma_newline_after,
            'value-list-comma-space-after': value_list_comma_space_after,
            'value-list-comma-space-before': value_list_comma_space_before,
            'value-list-max-empty-lines': value_list_max_empty_lines,
        }

        if not rules['at-rule-empty-line-before']:
            rules['at-rule-empty-line-before'] = [
                'always',
                {
                    'except': [
                        'blockless-after-same-name-blockless',
                        'first-nested'
                    ],
                    'ignore': [
                        'after-comment'
                    ]
                }
            ]

        if not rules['comment-empty-line-before']:
            rules['comment-empty-line-before'] = [
                'always',
                {
                    'except': [
                        'first-nested'
                    ],
                    'ignore': [
                        'stylelint-commands'
                    ]
                }
            ]

        if not rules['custom-property-empty-line-before']:
            rules['custom-property-empty-line-before'] = [
                'always',
                {
                    'except': [
                        'after-custom-property',
                        'first-nested'
                    ],
                    'ignore': [
                        'after-comment',
                        'inside-single-line-block'
                    ]
                }
            ]

        if not rules['declaration-block-no-duplicate-properties']:
            rules['declaration-block-no-duplicate-properties'] = [
                True,
                {
                    'ignore': [
                        'consecutive-duplicates-with-different-values'
                    ]
                }
            ]

        if not rules['declaration-empty-line-before']:
            rules['declaration-empty-line-before'] = [
                'always',
                {
                    'except': [
                        'after-declaration',
                        'first-nested'
                    ],
                    'ignore': [
                        'after-comment',
                        'inside-single-line-block'
                    ]
                }
            ]

        if not rules['rule-empty-line-before']:
            rules['rule-empty-line-before'] = [
                'always-multi-line',
                {
                    'except': [
                        'first-nested'
                    ],
                    'ignore': [
                        'after-comment'
                    ]
                }
            ]

        stylelint_config = {'rules': rules}
        return json.dumps(stylelint_config)

    @staticmethod
    def create_arguments(filename, file, config_file):
        return filename, '--config=' + config_file
