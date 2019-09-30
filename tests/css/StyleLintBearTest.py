import os
from queue import Queue
from shutil import which
from unittest.case import skipIf

from bears.css.StyleLintBear import StyleLintBear
from coalib.testing.LocalBearTestHelper import LocalBearTestHelper
from coalib.settings.Section import Section
from coalib.settings.Setting import Setting


at_rule_empty_line_before_good_file = """
a { color: pink; }
@media { color: pink; }
""".splitlines(True)

at_rule_empty_line_before_bad_file = """
a { color: pink; }

@media { color: pink; }
""".splitlines(True)

at_rule_name_case_good_file = """
@CHARSET 'UTF-8';
""".splitlines(True)

at_rule_name_case_bad_file = """
@cHarSeT 'UTF-8';
""".splitlines(True)

at_rule_name_space_after_good_file = """
@charset "UTF-8";

@import url("x.css");

@media (min-width: 700px) { color: pink; }
""".splitlines(True)

at_rule_name_space_after_bad_file = """
@charset"UTF-8";

@media(min-width: 700px) { color: pink; }

@media  (min-width: 700px) { color: pink; }
""".splitlines(True)

at_rule_semicolon_newline_after_good_file = """
@import url("x.css");
@import url("y.css");
""".splitlines(True)

at_rule_semicolon_newline_after_bad_file = """
@import url("x.css"); @import url("y.css");
""".splitlines(True)

block_closing_brace_empty_line_before_good_file = """
a {
  color: pink;

}
""".splitlines(True)

block_closing_brace_empty_line_before_bad_file = """
a {
  color: pink;
}
""".splitlines(True)

block_closing_brace_newline_after_good_file = """
a { color: pink; }b { color: red; }
""".splitlines(True)

block_closing_brace_newline_after_bad_file = """
a { color: pink; } b { color: red; }
""".splitlines(True)

block_closing_brace_newline_before_good_file = """
a { color: pink; }

a {
  color: pink;}
""".splitlines(True)

block_closing_brace_newline_before_bad_file = """
a {
  color: pink; }
""".splitlines(True)

block_closing_brace_space_before_good_file = """
a { color: pink;}
""".splitlines(True)

block_closing_brace_space_before_bad_file = """
a { color: pink; }
""".splitlines(True)

block_no_empty_good_file = """
a { color: pink; }

@media print { a { color: pink; } }
""".splitlines(True)

block_no_empty_bad_file = """
a { color: pink; }

a { }

@media print { a { color: pink; } }
""".splitlines(True)

block_opening_brace_newline_after_good_file = """
a { color: pink; }

a {color: pink;
}
""".splitlines(True)

block_opening_brace_newline_after_bad_file = """
a { color: pink;
}
""".splitlines(True)

block_opening_brace_space_after_good_file = """
a {color: pink; }
""".splitlines(True)

block_opening_brace_space_after_bad_file = """
a { color: pink; }
""".splitlines(True)

block_opening_brace_space_before_good_file = """
a{ color: pink; }
""".splitlines(True)

block_opening_brace_space_before_bad_file = """
a { color: pink; }
""".splitlines(True)

color_hex_case_good_file = """
a { color: #000; }

a { color: #FFF; }
""".splitlines(True)

color_hex_case_bad_file = """
a { color: #fff; }
""".splitlines(True)

color_hex_length_good_file = """
a { color: #ffffff; }

a { color: #ffffffaa; }
""".splitlines(True)

color_hex_length_bad_file = """
a { color: #fff; }

a { color: #fffa; }
""".splitlines(True)

color_no_invalid_hex_good_file = """
a { color: #000; }

a { color: #000f; }

a { color: #fff1a0; }

a { color: #123450aa; }
""".splitlines(True)

color_no_invalid_hex_bad_file = """
a { color: #00; }

a { color: #fff1az; }

a { color: #12345aa; }
""".splitlines(True)

comment_empty_line_before_good_file = """
a { color: pink; }
/* comment */

a { color: pink; } /* comment */
""".splitlines(True)

comment_empty_line_before_bad_file = """
a { color: pink; }

/* comment */
""".splitlines(True)

comment_no_empty_good_file = """
/* comment */

/*
 * Multi-line Comment
**/
""".splitlines(True)

comment_no_empty_bad_file = """
/**/

/* */

/*

 */
""".splitlines(True)

comment_whitespace_inside_good_file = """
/*comment*/

/****comment****/
""".splitlines(True)

comment_whitespace_inside_bad_file = """
/* comment */

/*comment */

/** comment**/
""".splitlines(True)

custom_property_empty_line_before_good_file = """
a {
  top: 10px;
  --foo: pink;
  --bar: red;
}
""".splitlines(True)

custom_property_empty_line_before_bad_file = """
a {
  top: 10px;

  --foo: pink;

  --bar: red;
}
""".splitlines(True)

declaration_bang_space_after_good_file = """
a { color: pink ! important; }
""".splitlines(True)

declaration_bang_space_after_bad_file = """
a { color: pink !important; }

a { color: pink      !important; }
""".splitlines(True)

declaration_bang_space_before_good_file = """
a { color: pink!important; }
""".splitlines(True)

declaration_bang_space_before_bad_file = """
a { color : pink !important; }
""".splitlines(True)

declaration_block_no_duplicate_properties_good_file = """
a {
  color: pink;
}

a {
  color: pink;
  background: orange;
}
""".splitlines(True)

declaration_block_no_duplicate_properties_bad_file = """
a {
  color: pink;
  color: orange;
}

a {
  color: pink;
  background: orange;
  color: orange
}
""".splitlines(True)

declaration_block_no_redundant_longhand_properties_good_file = """
a {
  margin: 1px 2px 3px 4px;
}
""".splitlines(True)

declaration_block_no_redundant_longhand_properties_bad_file = """
a {
  margin-top: 1px;
  margin-right: 2px;
  margin-bottom: 3px;
  margin-left: 4px;
}
""".splitlines(True)

declaration_block_no_shorthand_property_overrides_good_file = """
a { padding: 10px; }
""".splitlines(True)

declaration_block_no_shorthand_property_overrides_bad_file = """
a {
  padding-left: 10px;
  padding: 20px;
}
""".splitlines(True)

declaration_block_semicolon_newline_after_good_file = """
a {
  color: pink;
  top: 0;
}

a {
  color: pink; /* end-of-line comment */
  top: 0;
}
""".splitlines(True)

declaration_block_semicolon_newline_after_bad_file = """
a { color: pink; top: 0; }

a {
  color: pink; /* end-of-line comment
    containing a newline */
  top: 0;
}
""".splitlines(True)

declaration_block_semicolon_space_after_good_file = """
a { color: pink; }
""".splitlines(True)

declaration_block_semicolon_space_after_bad_file = """
a {
  color: pink;
  top: 0;
}
""".splitlines(True)

declaration_block_semicolon_space_before_good_file = """
a { color: black ; }
""".splitlines(True)

declaration_block_semicolon_space_before_bad_file = """
a { color: black; }
""".splitlines(True)

declaration_block_single_line_max_declarations_good_file = """
a { color: pink; top: 3px; }

a,
b { color: pink; top: 3px; }
""".splitlines(True)

declaration_block_single_line_max_declarations_bad_file = """
a { color: pink; top: 3px; bottom: 3px; }

a,
b { color: pink; top: 3px; bottom: 3px; }
""".splitlines(True)

declaration_block_trailing_semicolon_good_file = """
a { color: pink }
""".splitlines(True)

declaration_block_trailing_semicolon_bad_file = """
a { color: pink; }
""".splitlines(True)

declaration_colon_newline_after_good_file = """
a {
  color: pink;
}
""".splitlines(True)

declaration_colon_newline_after_bad_file = """
a {
  box-shadow: 0 0 0 1px #5b9dd9,
    0 0 2px 1px rgba(30, 140, 190, 0.8);
}
""".splitlines(True)

declaration_colon_space_after_good_file = """
a { color: pink; }
""".splitlines(True)

declaration_colon_space_after_bad_file = """
a { color:pink; }
""".splitlines(True)

declaration_colon_space_before_good_file = """
a { color : pink; }
""".splitlines(True)

declaration_colon_space_before_bad_file = """
a { color: pink; }
""".splitlines(True)

declaration_empty_line_before_good_file = """
a {
  --foo: pink;
  bottom: 15px;
}

a {
  bottom: 15px;
  top: 5px;
}
""".splitlines(True)

declaration_empty_line_before_bad_file = """
a {
  --foo: pink;

  bottom: 15px;
}

a {

  bottom: 15px;

  top: 5px;
}
""".splitlines(True)

font_family_no_duplicate_names_good_file = """
a { font-family: Times, serif; }

a { font: 1em "Arial", "sans-serif", sans-serif; }
""".splitlines(True)

font_family_no_duplicate_names_bad_file = """
a { font-family: 'Times', Times, serif; }

a { font: 1em "Arial", 'Arial', sans-serif; }
""".splitlines(True)

function_calc_no_unspaced_operator_good_file = """
a { top: calc(1px + 2px); }

a { top: calc(calc(1em * 2) / 3); }
""".splitlines(True)

function_calc_no_unspaced_operator_bad_file = """
a { top: calc(1px+2px); }

a { top: calc(1px+ 2px); }
""".splitlines(True)

function_comma_newline_after_good_file = """
a { transform: translate(1, 1); }
""".splitlines(True)

function_comma_newline_after_bad_file = """
a { transform: translate(1
  , 1); }
""".splitlines(True)

function_comma_space_after_good_file = """
a { transform: translate(1,1); }
""".splitlines(True)

function_comma_space_after_bad_file = """
a { transform: translate(1, 1); }
""".splitlines(True)

function_comma_space_before_good_file = """
a { transform: translate(1 , 1); }
""".splitlines(True)

function_comma_space_before_bad_file = """
a { transform: translate(1, 1); }
""".splitlines(True)

function_linear_gradient_no_nonstandard_direction_good_file = """
.foo { background: linear-gradient(to top, #fff, #000); }

.foo { background: linear-gradient(to bottom right, #fff, #000); }

.foo { background: linear-gradient(45deg, #fff, #000); }

.foo { background: linear-gradient(1.57rad, #fff, #000); }

/* Direction defaults to "to bottom" */
.foo { background: linear-gradient(#fff, #000); }
""".splitlines(True)

function_linear_gradient_no_nonstandard_direction_bad_file = """
.foo { background: linear-gradient(top, #fff, #000); }

.foo { background: linear-gradient(bottom, #fff, #000); }

.foo { background: linear-gradient(left, #fff, #000); }

.foo { background: linear-gradient(45, #fff, #000); }

.foo { background: linear-gradient(to top top, #fff, #000); }
""".splitlines(True)

function_max_empty_lines_good_file = """
a {
  transform:
    translate(
      1,
      1
    );
}
""".splitlines(True)

function_max_empty_lines_bad_file = """
a {
  transform:
    translate(

      1,
      1
    );
}
""".splitlines(True)

function_name_case_good_file = """
a {
  width: CALC(5% - 10em);
}

a {
  background: -WEBKIT-RADIAL-GRADIENT(red, green, blue);
}
""".splitlines(True)

function_name_case_bad_file = """
a {
  width: calc(5% - 10em);
}

a {
  background: -webkit-radial-gradient(red, green, blue);
}
""".splitlines(True)

function_parentheses_newline_inside_good_file = """
a { transform: translate(1, 1); }
""".splitlines(True)

function_parentheses_newline_inside_bad_file = """
a {
  transform: translate(
    1, 1
  );
}

a {
  transform: translate(
    1,
    1
  );
}
""".splitlines(True)

function_parentheses_space_inside_good_file = """
a { transform: translate( 1, 1 ); }
""".splitlines(True)

function_parentheses_space_inside_bad_file = """
a { transform: translate(1, 1); }

a { transform: translate(1, 1 ); }
""".splitlines(True)

function_whitespace_after_good_file = """
a { transform: translate(1, 1)scale(3); }
""".splitlines(True)

function_whitespace_after_bad_file = """
a { transform: translate(1, 1) scale(3); }
""".splitlines(True)

indentation_good_file = """
@media print {
  a {
    background-position: top left,
      top right;
  }
}
""".splitlines(True)


# The test fails here, it didn't emit any errors
indentation_bad_file = """
@media print {
a {
background-position: top left,
top right;
}
}
""".splitlines(True)

keyframe_declaration_no_important_good_file = """
@keyframes important1 {
  from {
    margin-top: 50px;
  }

  to {
    margin-top: 100px;
  }
}
""".splitlines(True)

keyframe_declaration_no_important_bad_file = """
@keyframes important1 {
  from {
    margin-top: 50px;
  }

  to {
    margin-top: 100px !important;
  }
}
""".splitlines(True)

length_zero_no_unit_good_file = """
a { top: 0; } /* no unit */

a { transition-delay: 0s; } /* dimension */

a { top: 2in; }

a { top: 1.001vh; }
""".splitlines(True)

length_zero_no_unit_bad_file = """
a { top: 0px; }

a { top: 0.000em; }
""".splitlines(True)

max_empty_lines_good_file = """
a { color: pink; }



b { color: pink; }
""".splitlines(True)

max_empty_lines_bad_file = """
a { color: pink; }




b { color: pink; }
""".splitlines(True)

media_feature_colon_space_after_good_file = """
@media (max-width:600px) { color: pink; }

@media (max-width:600px) { color: pink; }
""".splitlines(True)

media_feature_colon_space_after_bad_file = """
@media (max-width: 600px) { color: pink; }
""".splitlines(True)

media_feature_colon_space_before_good_file = """
@media (max-width : 600px) { color: pink; }
""".splitlines(True)

media_feature_colon_space_before_bad_file = """
@media (max-width:600px) { color: pink; }

@media (max-width: 600px) { color: pink; }
""".splitlines(True)

media_feature_name_case_good_file = """
@media (MIN-WIDTH: 700px) { color: pink; }

@media not all and (MONOCHROME) { color: pink; }

@media (MIN-WIDTH: 700px) and (ORIENTATION: landscape) { color: pink; }
""".splitlines(True)

media_feature_name_case_bad_file = """
@media (min-width: 700px) { color: pink; }

@media not all and (monochrome) { color: pink; }

@media (MIN-WIDTH: 700px) and (orientation: landscape) { color: pink; }
""".splitlines(True)

media_feature_name_no_unknown_good_file = """
@media all and (monochrome) { color: pink; }

@media (min-width: 700px) { color: pink; }
""".splitlines(True)

media_feature_name_no_unknown_bad_file = """
@media screen and (unknown) { color: pink; }

@media screen and (unknown: 10px) { color: pink; }
""".splitlines(True)

media_feature_parentheses_space_inside_good_file = """
@media ( max-width: 300px ) { color: pink; }
""".splitlines(True)

media_feature_parentheses_space_inside_bad_file = """
@media (max-width: 300px) { color: pink; }

@media (max-width: 300px ) { color: pink; }
""".splitlines(True)

media_feature_range_operator_space_after_good_file = """
@media (width >=600px) { color: pink; }
""".splitlines(True)

media_feature_range_operator_space_after_bad_file = """
@media (width >= 600px) { color: pink; }
""".splitlines(True)

media_feature_range_operator_space_before_good_file = """
@media (width>= 600px) { color: pink; }
""".splitlines(True)

media_feature_range_operator_space_before_bad_file = """
@media (width >= 600px) { color: pink; }
""".splitlines(True)

media_query_list_comma_newline_after_good_file = """
@media screen and (color), projection and (color) { color: pink; }
""".splitlines(True)

media_query_list_comma_newline_after_bad_file = """
@media screen and (color)
, projection and (color) { color: pink; }
""".splitlines(True)

media_query_list_comma_space_after_good_file = """
@media screen and (color), projection and (color) { color: pink; }
""".splitlines(True)

media_query_list_comma_space_after_bad_file = """
@media screen and (color),projection and (color) { color: pink; }
""".splitlines(True)

media_query_list_comma_space_before_good_file = """
@media screen and (color) , projection and (color) { color: pink; }

@media screen and (color) ,
  projection and (color) { color: pink; }
""".splitlines(True)

media_query_list_comma_space_before_bad_file = """
@media screen and (color),projection and (color) { color: pink; }

@media screen and (color)
,projection and (color) { color: pink; }
""".splitlines(True)

no_empty_source_good_file = """
/* Only comments */
""".splitlines(True)

no_empty_source_bad_file = """
\t\t
""".splitlines(True)

no_eol_whitespace_good_file = """
a { color: pink; }

/* something
 * something else */
""".splitlines(True)

# start ignoring SpaceConsistencyBear, PycodestyleBear
no_eol_whitespace_bad_file = """
a { color: pink; } 

a { color: pink; }    

/* something    
 * something else */
""".splitlines(True)
# stop ignoring

no_extra_semicolons_good_file = """
@import "x.css";

a {
  color: pink;
}
""".splitlines(True)

no_extra_semicolons_bad_file = """
@import "x.css";;

@import "x.css";
;

a {
  color: pink;;
}

a {
  ;color: pink;
}
""".splitlines(True)

no_invalid_double_slash_comments_good_file = """
a { /* color: pink; */ }

/* a { color: pink; } */
""".splitlines(True)

no_invalid_double_slash_comments_bad_file = """
a { // color: pink; }

// a { color: pink; }
""".splitlines(True)

no_missing_end_of_source_newline_good_file = """
a { color: pink; }
""".splitlines(True)

# The test fails here, it didn't emit any errors
no_missing_end_of_source_newline_bad_file = ['a { color: pink; }']

number_leading_zero_good_file = """
a { line-height: .5; }

a { transform: translate(2px, .4px); }
""".splitlines(True)

number_leading_zero_bad_file = """
a { line-height: 0.5; }

a { transform: translate(2px, 0.4px); }
""".splitlines(True)

number_no_trailing_zeros_good_file = """
a { top: 1px; }

a { top: 1.01px; }
""".splitlines(True)

number_no_trailing_zeros_bad_file = """
a { top: 1.0px; }

a { top: 1.01000px; }
""".splitlines(True)

property_case_good_file = """
a {
  WIDTH: 1px;
}
""".splitlines(True)

property_case_bad_file = """
a {
  widtH: 1px;
}
""".splitlines(True)

property_no_unknown_good_file = """
a {
  color: green;
}

a {
  fill: black;
}
""".splitlines(True)

property_no_unknown_bad_file = """
a {
  colr: blue;
}

a {
  my-property: 1;
}
""".splitlines(True)

rule_empty_line_before_good_file = """
a {
  color: red;
}
b {
  color: blue;
}
""".splitlines(True)

rule_empty_line_before_bad_file = """
a {
  color: red;
}

b {
  color: blue;
}
""".splitlines(True)

selector_attribute_brackets_space_inside_good_file = """
[ target ] { color: pink; }

[ target=_blank ] { color: pink; }
""".splitlines(True)

selector_attribute_brackets_space_inside_bad_file = """
[target ] { color: pink; }

[target=_blank] { color: pink; }
""".splitlines(True)

selector_attribute_operator_space_after_good_file = """
[target] { color: pink; }

[target= _blank] { color: pink; }

[target= '_blank'] { color: pink; }

[target= "_blank"] { color: pink; }
""".splitlines(True)

selector_attribute_operator_space_after_bad_file = """
[target=_blank] { color: pink; }

[target =_blank] { color: pink; }

[target ='_blank'] { color: pink; }

[target ="_blank"] { color: pink; }
""".splitlines(True)

selector_attribute_operator_space_before_good_file = """
[target] { color: pink; }

[target =_blank] { color: pink; }

[target ='_blank'] { color: pink; }

[target ="_blank"] { color: pink; }
""".splitlines(True)

selector_attribute_operator_space_before_bad_file = """
[target=_blank] { color: pink; }

[target='_blank'] { color: pink; }

[target="_blank"] { color: pink; }
""".splitlines(True)

selector_combinator_space_after_good_file = """
a +b { color: pink; }

a >b { color: pink; }
""".splitlines(True)

selector_combinator_space_after_bad_file = """
a + b { color: pink; }

a > b { color: pink; }
""".splitlines(True)

selector_combinator_space_before_good_file = """
a+ b { color: pink; }

a> b { color: pink; }
""".splitlines(True)

selector_combinator_space_before_bad_file = """
a +b { color: pink; }

a >b { color: pink; }
""".splitlines(True)

selector_descendant_combinator_no_non_space_good_file = """
.foo .bar { color: pink; }
""".splitlines(True)

selector_descendant_combinator_no_non_space_bad_file = """
.foo  .bar { color: pink; }

.foo
.bar { color: pink; }
""".splitlines(True)

selector_list_comma_newline_after_good_file = """
a,b { color: pink; }
""".splitlines(True)

selector_list_comma_newline_after_bad_file = """
a
, b { color: pink; }

a,
b { color: pink; }
""".splitlines(True)

selector_list_comma_space_before_good_file = """
a ,
b { color: pink; }
""".splitlines(True)

selector_list_comma_space_before_bad_file = """
a, b { color: pink; }
""".splitlines(True)

selector_max_empty_lines_good_file = """
a b {
  color: red;
}
""".splitlines(True)

selector_max_empty_lines_bad_file = """
a

b {
  color: red;
}
""".splitlines(True)

selector_pseudo_class_case_good_file = """
a:HOVER { color: pink; }

:ROOT { color: pink; }

:-MS-INPUT-PLACEHOLDER { color: pink; }
""".splitlines(True)

selector_pseudo_class_case_bad_file = """
a:Hover { color: pink; }

a:hOvEr { color: pink; }

a:hover { color: pink; }

:root { color: pink; }

:-ms-input-placeholder { color: pink; }
""".splitlines(True)

selector_pseudo_class_no_unknown_good_file = """
a:hover { color: pink; }

a:focus { color: pink; }

:not(p) { color: pink; }

input:-moz-placeholder { color: pink; }
""".splitlines(True)

selector_pseudo_class_no_unknown_bad_file = """
a:unknown { color: pink; }

a:UNKNOWN { color: pink; }

a:hoverr { color: pink; }
""".splitlines(True)

selector_pseudo_class_parentheses_space_inside_good_file = """
input:not( [type="submit"] ) { color: pink; }
""".splitlines(True)

selector_pseudo_class_parentheses_space_inside_bad_file = """
input:not([type="submit"]) { color: pink; }

input:not([type="submit"] ) { color: pink; }
""".splitlines(True)

selector_pseudo_element_case_good_file = """
a::BEFORE { color: pink; }

input::-MOZ-PLACEHOLDER { color: pink; }
""".splitlines(True)

selector_pseudo_element_case_bad_file = """
a:Before { color: pink; }

a:bEfOrE { color: pink; }

a:BEFORE { color: pink; }

a::Before { color: pink; }

a::bEfOrE { color: pink; }

a::before { color: pink; }

input::-moz-placeholder { color: pink; }
""".splitlines(True)

selector_pseudo_element_colon_notation_good_file = """
a:before { color: pink; }

a:after { color: pink; }

a:first-letter { color: pink; }

a:first-line { color: pink; }

input::placeholder { color: pink; }

li::marker { font-variant-numeric: tabular-nums; }
""".splitlines(True)

selector_pseudo_element_colon_notation_bad_file = """
a::before { color: pink; }

a::after { color: pink; }

a::first-letter { color: pink; }

a::first-line { color: pink; }
""".splitlines(True)

selector_pseudo_element_no_unknown_good_file = """
a::before { color: pink; }

::selection { color: pink; }

input::-moz-placeholder { color: pink; }
""".splitlines(True)

selector_pseudo_element_no_unknown_bad_file = """
a::pseudo { color: pink; }

a::PSEUDO { color: pink; }

a::element { color: pink; }
""".splitlines(True)

selector_type_case_good_file = """
A { color: pink; }

LI { color: pink; }
""".splitlines(True)

selector_type_case_bad_file = """
a { color: pink; }

li { color: pink; }
""".splitlines(True)

selector_type_no_unknown_good_file = """
input { color: pink; }

ul li { color: pink; }

li > a { color: pink; }
""".splitlines(True)

selector_type_no_unknown_bad_file = """
unknown { color: pink; }

tag { color: pink; }
""".splitlines(True)

shorthand_property_no_redundant_values_good_file = """
a { margin: 1px; }

a { margin: 1px 1px 1px 2px; }

a { padding: 1px 1em 1pt 1pc; }

a { border-radius: 10px / 5px; }
""".splitlines(True)

shorthand_property_no_redundant_values_bad_file = """
a { margin: 1px 1px; }

a { margin: 1px 1px 1px 1px; }

a { padding: 1px 2px 1px; }

a { border-radius: 1px 2px 1px 2px; }

a { -webkit-border-radius: 1px 1px 1px 1px; }
""".splitlines(True)

string_no_newline_good_file = """
a {
  font-family: "Times New Roman";
}
""".splitlines(True)

string_no_newline_bad_file = """
a {
  font-family: "Times
    New
    Roman";
}
""".splitlines(True)

unit_case_good_file = """
a {
  width: 10PX;
}

a {
  width: calc(10PX * 2);
}
""".splitlines(True)

unit_case_bad_file = """
a {
  width: 10px;
}

a {
  width: 10Px;
}

a {
  width: 10pX;
}

a {
  width: 10pixel;
}

a {
  width: calc(10px * 2);
}
""".splitlines(True)

unit_no_unknown_good_file = """
a {
  width: 10px;
}

a {
  width: calc(10px + 10px);
}
""".splitlines(True)

unit_no_unknown_bad_file = """
a {
  width: 10pixels;
}

a {
  width: calc(10px + 10pixels);
}
""".splitlines(True)

value_list_comma_newline_after_good_file = """
a { background-size: 0, 0; }
""".splitlines(True)

value_list_comma_newline_after_bad_file = """
a { background-size: 0
      , 0; }
""".splitlines(True)

value_list_comma_space_after_good_file = """
a { background-size: 0, 0; }
""".splitlines(True)

value_list_comma_space_after_bad_file = """
a { background-size: 0,0; }

a { background-size: 0
      , 0; }
""".splitlines(True)

value_list_comma_space_before_good_file = """
a { background-size: 0 , 0; }
""".splitlines(True)

value_list_comma_space_before_bad_file = """
a { background-size: 0,0; }
""".splitlines(True)

value_list_max_empty_lines_good_file = """
a {
  box-shadow:
    inset 0 2px 0 #dcffa6,
    0 2px 5px #000;
}
""".splitlines(True)

value_list_max_empty_lines_bad_file = """
a {
  box-shadow:
    inset 0 2px 0 #dcffa6,

    0 2px 5px #000;
}
""".splitlines(True)


def get_testfile_path(name):
    return os.path.join(os.path.dirname(__file__),
                        'test_files',
                        name)


@skipIf(which('stylelint') is None, 'Stylelint is not installed')
class StyleLintBearTest(LocalBearTestHelper):

    def setUp(self):
        self.section = Section('')
        self.uut = StyleLintBear(self.section, Queue())
        test_files = os.path.join(os.path.dirname(__file__), 'test_files')
        self.good_file = os.path.join(test_files, 'stylelint_good.css')
        self.bad_file = os.path.join(test_files, 'stylelint_bad.css')

    def test_run(self):
        self.check_validity(self.uut, [], self.good_file)
        self.check_invalidity(self.uut, [], self.bad_file)

    def test_at_rule_empty_line_before(self):
        self.section.append(
            Setting('at_rule_empty_line_before',
                    'never'))
        self.check_validity(
            self.uut,
            at_rule_empty_line_before_good_file)
        self.check_invalidity(
            self.uut,
            at_rule_empty_line_before_bad_file)

    def test_at_rule_name_case(self):
        self.section.append(
            Setting('at_rule_name_case',
                    'upper'))
        self.check_validity(
            self.uut,
            at_rule_name_case_good_file)
        self.check_invalidity(
            self.uut,
            at_rule_name_case_bad_file)

    def test_at_rule_name_space_after(self):
        self.section.append(
            Setting('at_rule_name_space_after',
                    'always'))
        self.check_validity(
            self.uut,
            at_rule_name_space_after_good_file)
        self.check_invalidity(
            self.uut,
            at_rule_name_space_after_bad_file)

    def test_at_rule_semicolon_newline_after(self):
        self.section.append(
            Setting('at_rule_semicolon_newline_after',
                    'always'))
        self.check_validity(
            self.uut,
            at_rule_semicolon_newline_after_good_file)
        self.check_invalidity(
            self.uut,
            at_rule_semicolon_newline_after_bad_file)

    def test_block_closing_brace_empty_line_before(self):
        self.section.append(
            Setting('block_closing_brace_empty_line_before',
                    'always-multi-line'))
        self.check_validity(
            self.uut,
            block_closing_brace_empty_line_before_good_file)
        self.check_invalidity(
            self.uut,
            block_closing_brace_empty_line_before_bad_file)

    def test_block_closing_brace_newline_after(self):
        self.section.append(
            Setting('block_closing_brace_newline_after',
                    'never-single-line'))
        self.check_validity(
            self.uut,
            block_closing_brace_newline_after_good_file)
        self.check_invalidity(
            self.uut,
            block_closing_brace_newline_after_bad_file)

    def test_block_closing_brace_newline_before(self):
        self.section.append(
            Setting('block_closing_brace_newline_before',
                    'never-multi-line'))
        self.check_validity(
            self.uut,
            block_closing_brace_newline_before_good_file)
        self.check_invalidity(
            self.uut,
            block_closing_brace_newline_before_bad_file)

    def test_block_closing_brace_space_before(self):
        self.section.append(
            Setting('block_closing_brace_space_before',
                    'never-single-line'))
        self.check_validity(
            self.uut,
            block_closing_brace_space_before_good_file)
        self.check_invalidity(
            self.uut,
            block_closing_brace_space_before_bad_file)

    def test_block_no_empty(self):
        self.section.append(
            Setting('block_no_empty',
                    True))
        self.check_validity(
            self.uut,
            block_no_empty_good_file)
        self.check_invalidity(
            self.uut,
            block_no_empty_bad_file)

    def test_block_opening_brace_newline_after(self):
        self.section.append(
            Setting('block_opening_brace_newline_after',
                    'never-multi-line'))
        self.check_validity(
            self.uut,
            block_opening_brace_newline_after_good_file)
        self.check_invalidity(
            self.uut,
            block_opening_brace_newline_after_bad_file)

    def test_block_opening_brace_space_after(self):
        self.section.append(
            Setting('block_opening_brace_space_after',
                    'never-single-line'))
        self.check_validity(
            self.uut,
            block_opening_brace_space_after_good_file)
        self.check_invalidity(
            self.uut,
            block_opening_brace_space_after_bad_file)

    def test_block_opening_brace_space_before(self):
        self.section.append(
            Setting('block_opening_brace_space_before',
                    'never'))
        self.check_validity(
            self.uut,
            block_opening_brace_space_before_good_file)
        self.check_invalidity(
            self.uut,
            block_opening_brace_space_before_bad_file)

    def test_color_hex_case(self):
        self.section.append(
            Setting('color_hex_case',
                    'upper'))
        self.check_validity(
            self.uut,
            color_hex_case_good_file)
        self.check_invalidity(
            self.uut,
            color_hex_case_bad_file)

    def test_color_hex_length(self):
        self.section.append(
            Setting('color_hex_length',
                    'long'))
        self.check_validity(
            self.uut,
            color_hex_length_good_file)
        self.check_invalidity(
            self.uut,
            color_hex_length_bad_file)

    def test_color_no_invalid_hex(self):
        self.section.append(
            Setting('color_no_invalid_hex',
                    True))
        self.check_validity(
            self.uut,
            color_no_invalid_hex_good_file)
        self.check_invalidity(
            self.uut,
            color_no_invalid_hex_bad_file)

    def test_comment_empty_line_before(self):
        self.section.append(
            Setting('comment_empty_line_before',
                    'never'))
        self.check_validity(
            self.uut,
            comment_empty_line_before_good_file)
        self.check_invalidity(
            self.uut,
            comment_empty_line_before_bad_file)

    def test_comment_no_empty(self):
        self.section.append(
            Setting('comment_no_empty',
                    True))
        self.check_validity(
            self.uut,
            comment_no_empty_good_file)
        self.check_invalidity(
            self.uut,
            comment_no_empty_bad_file)

    def test_comment_whitespace_inside(self):
        self.section.append(
            Setting('comment_whitespace_inside',
                    'never'))
        self.check_validity(
            self.uut,
            comment_whitespace_inside_good_file)
        self.check_invalidity(
            self.uut,
            comment_whitespace_inside_bad_file)

    def test_custom_property_empty_line_before(self):
        self.section.append(
            Setting('custom_property_empty_line_before',
                    'never'))
        self.check_validity(
            self.uut,
            custom_property_empty_line_before_good_file)
        self.check_invalidity(
            self.uut,
            custom_property_empty_line_before_bad_file)

    def test_declaration_bang_space_after(self):
        self.section.append(
            Setting('declaration_bang_space_after',
                    'always'))
        self.check_validity(
            self.uut,
            declaration_bang_space_after_good_file)
        self.check_invalidity(
            self.uut,
            declaration_bang_space_after_bad_file)

    def test_declaration_bang_space_before(self):
        self.section.append(
            Setting('declaration_bang_space_before',
                    'never'))
        self.check_validity(
            self.uut,
            declaration_bang_space_before_good_file)
        self.check_invalidity(
            self.uut,
            declaration_bang_space_before_bad_file)

    def test_declaration_block_no_duplicate_properties(self):
        self.section.append(
            Setting('declaration_block_no_duplicate_properties',
                    True))
        self.check_validity(
            self.uut,
            declaration_block_no_duplicate_properties_good_file)
        self.check_invalidity(
            self.uut,
            declaration_block_no_duplicate_properties_bad_file)

    def test_declaration_block_no_redundant_longhand_properties(self):
        self.section.append(
            Setting('declaration_block_no_redundant_longhand_properties',
                    True))
        self.check_validity(
            self.uut,
            declaration_block_no_redundant_longhand_properties_good_file)
        self.check_invalidity(
            self.uut,
            declaration_block_no_redundant_longhand_properties_bad_file)

    def test_declaration_block_no_shorthand_property_overrides(self):
        self.section.append(
            Setting('declaration_block_no_shorthand_property_overrides',
                    True))
        self.check_validity(
            self.uut,
            declaration_block_no_shorthand_property_overrides_good_file)
        self.check_invalidity(
            self.uut,
            declaration_block_no_shorthand_property_overrides_bad_file)

    def test_declaration_block_semicolon_newline_after(self):
        self.section.append(
            Setting('declaration_block_semicolon_newline_after',
                    'always'))
        self.check_validity(
            self.uut,
            declaration_block_semicolon_newline_after_good_file)
        self.check_invalidity(
            self.uut,
            declaration_block_semicolon_newline_after_bad_file)

    def test_declaration_block_semicolon_space_after(self):
        self.section.append(
            Setting('declaration_block_semicolon_space_after',
                    'never'))
        self.check_validity(
            self.uut,
            declaration_block_semicolon_space_after_good_file)
        self.check_invalidity(
            self.uut,
            declaration_block_semicolon_space_after_bad_file)

    def test_declaration_block_semicolon_space_before(self):
        self.section.append(
            Setting('declaration_block_semicolon_space_before',
                    'always'))
        self.check_validity(
            self.uut,
            declaration_block_semicolon_space_before_good_file)
        self.check_invalidity(
            self.uut,
            declaration_block_semicolon_space_before_bad_file)

    def test_declaration_block_single_line_max_declarations(self):
        self.section.append(
            Setting('declaration_block_single_line_max_declarations',
                    2))
        self.check_validity(
            self.uut,
            declaration_block_single_line_max_declarations_good_file)
        self.check_invalidity(
            self.uut,
            declaration_block_single_line_max_declarations_bad_file)

    def test_declaration_block_trailing_semicolon(self):
        self.section.append(
            Setting('declaration_block_trailing_semicolon',
                    'never'))
        self.check_validity(
            self.uut,
            declaration_block_trailing_semicolon_good_file)
        self.check_invalidity(
            self.uut,
            declaration_block_trailing_semicolon_bad_file)

    def test_declaration_colon_newline_after(self):
        self.section.append(
            Setting('declaration_colon_newline_after',
                    'always-multi-line'))
        self.check_validity(
            self.uut,
            declaration_colon_newline_after_good_file)
        self.check_invalidity(
            self.uut,
            declaration_colon_newline_after_bad_file)

    def test_declaration_colon_space_after(self):
        self.section.append(
            Setting('declaration_colon_space_after',
                    'always'))
        self.check_validity(
            self.uut,
            declaration_colon_space_after_good_file)
        self.check_invalidity(
            self.uut,
            declaration_colon_space_after_bad_file)

    def test_declaration_colon_space_before(self):
        self.section.append(
            Setting('declaration_colon_space_before',
                    'always'))
        self.check_validity(
            self.uut,
            declaration_colon_space_before_good_file)
        self.check_invalidity(
            self.uut,
            declaration_colon_space_before_bad_file)

    def test_declaration_empty_line_before(self):
        self.section.append(
            Setting('declaration_empty_line_before',
                    'never'))
        self.check_validity(
            self.uut,
            declaration_empty_line_before_good_file)
        self.check_invalidity(
            self.uut,
            declaration_empty_line_before_bad_file)

    def test_font_family_no_duplicate_names(self):
        self.section.append(
            Setting('font_family_no_duplicate_names',
                    True))
        self.check_validity(
            self.uut,
            font_family_no_duplicate_names_good_file)
        self.check_invalidity(
            self.uut,
            font_family_no_duplicate_names_bad_file)

    def test_function_calc_no_unspaced_operator(self):
        self.section.append(
            Setting('function_calc_no_unspaced_operator',
                    True))
        self.check_validity(
            self.uut,
            function_calc_no_unspaced_operator_good_file)
        self.check_invalidity(
            self.uut,
            function_calc_no_unspaced_operator_bad_file)

    def test_function_comma_newline_after(self):
        self.section.append(
            Setting('function_comma_newline_after',
                    'never-multi-line'))
        self.check_validity(
            self.uut,
            function_comma_newline_after_good_file)
        self.check_invalidity(
            self.uut,
            function_comma_newline_after_bad_file)

    def test_function_comma_space_after(self):
        self.section.append(
            Setting('function_comma_space_after',
                    'never-single-line'))
        self.check_validity(
            self.uut,
            function_comma_space_after_good_file)
        self.check_invalidity(
            self.uut,
            function_comma_space_after_bad_file)

    def test_function_comma_space_before(self):
        self.section.append(
            Setting('function_comma_space_before',
                    'always'))
        self.check_validity(
            self.uut,
            function_comma_space_before_good_file)
        self.check_invalidity(
            self.uut,
            function_comma_space_before_bad_file)

    def test_function_linear_gradient_no_nonstandard_direction(self):
        self.section.append(
            Setting('function_linear_gradient_no_nonstandard_direction',
                    True))
        self.check_validity(
            self.uut,
            function_linear_gradient_no_nonstandard_direction_good_file)
        self.check_invalidity(
            self.uut,
            function_linear_gradient_no_nonstandard_direction_bad_file)

    def test_function_max_empty_lines(self):
        self.section.append(
            Setting('function_max_empty_lines',
                    0))
        self.check_validity(
            self.uut,
            function_max_empty_lines_good_file)
        self.check_invalidity(
            self.uut,
            function_max_empty_lines_bad_file)

    def test_function_name_case(self):
        self.section.append(
            Setting('function_name_case',
                    'upper'))
        self.check_validity(
            self.uut,
            function_name_case_good_file)
        self.check_invalidity(
            self.uut,
            function_name_case_bad_file)

    def test_function_parentheses_newline_inside(self):
        self.section.append(
            Setting('function_parentheses_newline_inside',
                    'never-multi-line'))
        self.check_validity(
            self.uut,
            function_parentheses_newline_inside_good_file)
        self.check_invalidity(
            self.uut,
            function_parentheses_newline_inside_bad_file)

    def test_function_parentheses_space_inside(self):
        self.section.append(
            Setting('function_parentheses_space_inside',
                    'always-single-line'))
        self.check_validity(
            self.uut,
            function_parentheses_space_inside_good_file)
        self.check_invalidity(
            self.uut,
            function_parentheses_space_inside_bad_file)

    def test_function_whitespace_after(self):
        self.section.append(
            Setting('function_whitespace_after',
                    'never'))
        self.check_validity(
            self.uut,
            function_whitespace_after_good_file)
        self.check_invalidity(
            self.uut,
            function_whitespace_after_bad_file)

    def test_indentation(self):
        self.section.append(
            Setting('indentation',
                    2))
        self.check_validity(
            self.uut,
            indentation_good_file,
            force_linebreaks=False)
        self.check_invalidity(
            self.uut,
            indentation_bad_file,
            force_linebreaks=False)

    def test_keyframe_declaration_no_important(self):
        self.section.append(
            Setting('keyframe_declaration_no_important',
                    True))
        self.check_validity(
            self.uut,
            keyframe_declaration_no_important_good_file)
        self.check_invalidity(
            self.uut,
            keyframe_declaration_no_important_bad_file)

    def test_length_zero_no_unit(self):
        self.section.append(
            Setting('length_zero_no_unit',
                    True))
        self.check_validity(
            self.uut,
            length_zero_no_unit_good_file)
        self.check_invalidity(
            self.uut,
            length_zero_no_unit_bad_file)

    def test_max_empty_lines(self):
        self.section.append(
            Setting('max_empty_lines',
                    3))
        self.check_validity(
            self.uut,
            max_empty_lines_good_file)
        self.check_invalidity(
            self.uut,
            max_empty_lines_bad_file)

    def test_media_feature_colon_space_after(self):
        self.section.append(
            Setting('media_feature_colon_space_after',
                    'never'))
        self.check_validity(
            self.uut,
            media_feature_colon_space_after_good_file)
        self.check_invalidity(
            self.uut,
            media_feature_colon_space_after_bad_file)

    def test_media_feature_colon_space_before(self):
        self.section.append(
            Setting('media_feature_colon_space_before',
                    'always'))
        self.check_validity(
            self.uut,
            media_feature_colon_space_before_good_file)
        self.check_invalidity(
            self.uut,
            media_feature_colon_space_before_bad_file)

    def test_media_feature_name_case(self):
        self.section.append(
            Setting('media_feature_name_case',
                    'upper'))
        self.check_validity(
            self.uut,
            media_feature_name_case_good_file)
        self.check_invalidity(
            self.uut,
            media_feature_name_case_bad_file)

    def test_media_feature_name_no_unknown(self):
        self.section.append(
            Setting('media_feature_name_no_unknown',
                    True))
        self.check_validity(
            self.uut,
            media_feature_name_no_unknown_good_file)
        self.check_invalidity(
            self.uut,
            media_feature_name_no_unknown_bad_file)

    def test_media_feature_parentheses_space_inside(self):
        self.section.append(
            Setting('media_feature_parentheses_space_inside',
                    'always'))
        self.check_validity(
            self.uut,
            media_feature_parentheses_space_inside_good_file)
        self.check_invalidity(
            self.uut,
            media_feature_parentheses_space_inside_bad_file)

    def test_media_feature_range_operator_space_after(self):
        self.section.append(
            Setting('media_feature_range_operator_space_after',
                    'never'))
        self.check_validity(
            self.uut,
            media_feature_range_operator_space_after_good_file)
        self.check_invalidity(
            self.uut,
            media_feature_range_operator_space_after_bad_file)

    def test_media_feature_range_operator_space_before(self):
        self.section.append(
            Setting('media_feature_range_operator_space_before',
                    'never'))
        self.check_validity(
            self.uut,
            media_feature_range_operator_space_before_good_file)
        self.check_invalidity(
            self.uut,
            media_feature_range_operator_space_before_bad_file)

    def test_media_query_list_comma_newline_after(self):
        self.section.append(
            Setting('media_query_list_comma_newline_after',
                    'always-multi-line'))
        self.check_validity(
            self.uut,
            media_query_list_comma_newline_after_good_file)
        self.check_invalidity(
            self.uut,
            media_query_list_comma_newline_after_bad_file)

    def test_media_query_list_comma_space_after(self):
        self.section.append(
            Setting('media_query_list_comma_space_after',
                    'always-single-line'))
        self.check_validity(
            self.uut,
            media_query_list_comma_space_after_good_file)
        self.check_invalidity(
            self.uut,
            media_query_list_comma_space_after_bad_file)

    def test_media_query_list_comma_space_before(self):
        self.section.append(
            Setting('media_query_list_comma_space_before',
                    'always'))
        self.check_validity(
            self.uut,
            media_query_list_comma_space_before_good_file)
        self.check_invalidity(
            self.uut,
            media_query_list_comma_space_before_bad_file)

    def test_no_empty_source(self):
        self.section.append(
            Setting('no_empty_source',
                    True))
        self.check_validity(
            self.uut,
            no_empty_source_good_file)
        self.check_invalidity(
            self.uut,
            no_empty_source_bad_file)

    def test_no_eol_whitespace(self):
        self.section.append(
            Setting('no_eol_whitespace',
                    True))
        self.check_validity(
            self.uut,
            no_eol_whitespace_good_file)
        self.check_invalidity(
            self.uut,
            no_eol_whitespace_bad_file)

    def test_no_extra_semicolons(self):
        self.section.append(
            Setting('no_extra_semicolons',
                    True))
        self.check_validity(
            self.uut,
            no_extra_semicolons_good_file)
        self.check_invalidity(
            self.uut,
            no_extra_semicolons_bad_file)

    def test_no_invalid_double_slash_comments(self):
        self.section.append(
            Setting('no_invalid_double_slash_comments',
                    True))
        self.check_validity(
            self.uut,
            no_invalid_double_slash_comments_good_file)
        self.check_invalidity(
            self.uut,
            no_invalid_double_slash_comments_bad_file)

    def test_no_missing_end_of_source_newline(self):
        self.section.append(
            Setting('no_missing_end_of_source_newline',
                    True))
        self.check_validity(
            self.uut,
            no_missing_end_of_source_newline_good_file,
            force_linebreaks=False)
        self.check_invalidity(
            self.uut,
            no_missing_end_of_source_newline_bad_file,
            force_linebreaks=False)

    def test_number_leading_zero(self):
        self.section.append(
            Setting('number_leading_zero',
                    'never'))
        self.check_validity(
            self.uut,
            number_leading_zero_good_file)
        self.check_invalidity(
            self.uut,
            number_leading_zero_bad_file)

    def test_number_no_trailing_zeros(self):
        self.section.append(
            Setting('number_no_trailing_zeros',
                    True))
        self.check_validity(
            self.uut,
            number_no_trailing_zeros_good_file)
        self.check_invalidity(
            self.uut,
            number_no_trailing_zeros_bad_file)

    def test_property_case(self):
        self.section.append(
            Setting('property_case',
                    'upper'))
        self.check_validity(
            self.uut,
            property_case_good_file)
        self.check_invalidity(
            self.uut,
            property_case_bad_file)

    def test_property_no_unknown(self):
        self.section.append(
            Setting('property_no_unknown',
                    True))
        self.check_validity(
            self.uut,
            property_no_unknown_good_file)
        self.check_invalidity(
            self.uut,
            property_no_unknown_bad_file)

    def test_rule_empty_line_before(self):
        self.section.append(
            Setting('rule_empty_line_before',
                    'never-multi-line'))
        self.check_validity(
            self.uut,
            rule_empty_line_before_good_file)
        self.check_invalidity(
            self.uut,
            rule_empty_line_before_bad_file)

    def test_selector_attribute_brackets_space_inside(self):
        self.section.append(
            Setting('selector_attribute_brackets_space_inside',
                    'always'))
        self.check_validity(
            self.uut,
            selector_attribute_brackets_space_inside_good_file)
        self.check_invalidity(
            self.uut,
            selector_attribute_brackets_space_inside_bad_file)

    def test_selector_attribute_operator_space_after(self):
        self.section.append(
            Setting('selector_attribute_operator_space_after',
                    'always'))
        self.check_validity(
            self.uut,
            selector_attribute_operator_space_after_good_file)
        self.check_invalidity(
            self.uut,
            selector_attribute_operator_space_after_bad_file)

    def test_selector_attribute_operator_space_before(self):
        self.section.append(
            Setting('selector_attribute_operator_space_before',
                    'always'))
        self.check_validity(
            self.uut,
            selector_attribute_operator_space_before_good_file)
        self.check_invalidity(
            self.uut,
            selector_attribute_operator_space_before_bad_file)

    def test_selector_combinator_space_after(self):
        self.section.append(
            Setting('selector_combinator_space_after',
                    'never'))
        self.check_validity(
            self.uut,
            selector_combinator_space_after_good_file)
        self.check_invalidity(
            self.uut,
            selector_combinator_space_after_bad_file)

    def test_selector_combinator_space_before(self):
        self.section.append(
            Setting('selector_combinator_space_before',
                    'never'))
        self.check_validity(
            self.uut,
            selector_combinator_space_before_good_file)
        self.check_invalidity(
            self.uut,
            selector_combinator_space_before_bad_file)

    def test_selector_descendant_combinator_no_non_space(self):
        self.section.append(
            Setting('selector_descendant_combinator_no_non_space',
                    True))
        self.check_validity(
            self.uut,
            selector_descendant_combinator_no_non_space_good_file)
        self.check_invalidity(
            self.uut,
            selector_descendant_combinator_no_non_space_bad_file)

    def test_selector_list_comma_newline_after(self):
        self.section.append(
            Setting('selector_list_comma_newline_after',
                    'never-multi-line'))
        self.check_validity(
            self.uut,
            selector_list_comma_newline_after_good_file)
        self.check_invalidity(
            self.uut,
            selector_list_comma_newline_after_bad_file)

    def test_selector_list_comma_space_before(self):
        self.section.append(
            Setting('selector_list_comma_space_before',
                    'always'))
        self.check_validity(
            self.uut,
            selector_list_comma_space_before_good_file)
        self.check_invalidity(
            self.uut,
            selector_list_comma_space_before_bad_file)

    def test_selector_max_empty_lines(self):
        self.section.append(
            Setting('selector_max_empty_lines',
                    0))
        self.check_validity(
            self.uut,
            selector_max_empty_lines_good_file)
        self.check_invalidity(
            self.uut,
            selector_max_empty_lines_bad_file)

    def test_selector_pseudo_class_case(self):
        self.section.append(
            Setting('selector_pseudo_class_case',
                    'upper'))
        self.check_validity(
            self.uut,
            selector_pseudo_class_case_good_file)
        self.check_invalidity(
            self.uut,
            selector_pseudo_class_case_bad_file)

    def test_selector_pseudo_class_no_unknown(self):
        self.section.append(
            Setting('selector_pseudo_class_no_unknown',
                    True))
        self.check_validity(
            self.uut,
            selector_pseudo_class_no_unknown_good_file)
        self.check_invalidity(
            self.uut,
            selector_pseudo_class_no_unknown_bad_file)

    def test_selector_pseudo_class_parentheses_space_inside(self):
        self.section.append(
            Setting('selector_pseudo_class_parentheses_space_inside',
                    'always'))
        self.check_validity(
            self.uut,
            selector_pseudo_class_parentheses_space_inside_good_file)
        self.check_invalidity(
            self.uut,
            selector_pseudo_class_parentheses_space_inside_bad_file)

    def test_selector_pseudo_element_case(self):
        self.section.append(
            Setting('selector_pseudo_element_case',
                    'upper'))
        self.check_validity(
            self.uut,
            selector_pseudo_element_case_good_file)
        self.check_invalidity(
            self.uut,
            selector_pseudo_element_case_bad_file)

    def test_selector_pseudo_element_colon_notation(self):
        self.section.append(
            Setting('selector_pseudo_element_colon_notation',
                    'single'))
        self.check_validity(
            self.uut,
            selector_pseudo_element_colon_notation_good_file)
        self.check_invalidity(
            self.uut,
            selector_pseudo_element_colon_notation_bad_file)

    def test_selector_pseudo_element_no_unknown(self):
        self.section.append(
            Setting('selector_pseudo_element_no_unknown',
                    True))
        self.check_validity(
            self.uut,
            selector_pseudo_element_no_unknown_good_file)
        self.check_invalidity(
            self.uut,
            selector_pseudo_element_no_unknown_bad_file)

    def test_selector_type_case(self):
        self.section.append(
            Setting('selector_type_case',
                    'upper'))
        self.check_validity(
            self.uut,
            selector_type_case_good_file)
        self.check_invalidity(
            self.uut,
            selector_type_case_bad_file)

    def test_selector_type_no_unknown(self):
        self.section.append(
            Setting('selector_type_no_unknown',
                    True))
        self.check_validity(
            self.uut,
            selector_type_no_unknown_good_file)
        self.check_invalidity(
            self.uut,
            selector_type_no_unknown_bad_file)

    def test_shorthand_property_no_redundant_values(self):
        self.section.append(
            Setting('shorthand_property_no_redundant_values',
                    True))
        self.check_validity(
            self.uut,
            shorthand_property_no_redundant_values_good_file)
        self.check_invalidity(
            self.uut,
            shorthand_property_no_redundant_values_bad_file)

    def test_string_no_newline(self):
        self.section.append(
            Setting('string_no_newline',
                    False))
        self.check_validity(
            self.uut,
            string_no_newline_good_file)
        self.check_invalidity(
            self.uut,
            string_no_newline_bad_file)

    def test_unit_case(self):
        self.section.append(
            Setting('unit_case',
                    'upper'))
        self.check_validity(
            self.uut,
            unit_case_good_file)
        self.check_invalidity(
            self.uut,
            unit_case_bad_file)

    def test_unit_no_unknown(self):
        self.section.append(
            Setting('unit_no_unknown',
                    True))
        self.check_validity(
            self.uut,
            unit_no_unknown_good_file)
        self.check_invalidity(
            self.uut,
            unit_no_unknown_bad_file)

    def test_value_list_comma_newline_after(self):
        self.section.append(
            Setting('value_list_comma_newline_after',
                    'never-multi-line'))
        self.check_validity(
            self.uut,
            value_list_comma_newline_after_good_file)
        self.check_invalidity(
            self.uut,
            value_list_comma_newline_after_bad_file)

    def test_value_list_comma_space_after(self):
        self.section.append(
            Setting('value_list_comma_space_after',
                    'always'))
        self.check_validity(
            self.uut,
            value_list_comma_space_after_good_file)
        self.check_invalidity(
            self.uut,
            value_list_comma_space_after_bad_file)

    def test_value_list_comma_space_before(self):
        self.section.append(
            Setting('value_list_comma_space_before',
                    'always'))
        self.check_validity(
            self.uut,
            value_list_comma_space_before_good_file)
        self.check_invalidity(
            self.uut,
            value_list_comma_space_before_bad_file)

    def test_value_list_max_empty_lines(self):
        self.section.append(
            Setting('value_list_max_empty_lines',
                    0))
        self.check_validity(
            self.uut,
            value_list_max_empty_lines_good_file)
        self.check_invalidity(
            self.uut,
            value_list_max_empty_lines_bad_file)
