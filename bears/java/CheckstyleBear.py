from coalib.bearlib.abstractions.Linter import linter
from coalib.settings.Setting import path
from dependency_management.requirements.DistributionRequirement import (
    DistributionRequirement)


_online_styles = {
    'android-check-easy': 'https://raw.githubusercontent.com/noveogroup/' +
    'android-check/master/android-check-plugin/src/main/resources/' +
    'checkstyle/checkstyle-easy.xml',
    'android-check-hard': 'https://raw.githubusercontent.com/noveogroup/' +
    'android-check/master/android-check-plugin/src/main/resources/' +
    'checkstyle/checkstyle-hard.xml',
}

_checkstyle_version = '6.19'

# To be deprecated
known_checkstyles = dict(_online_styles, **{'google': None, 'sun': None})


def check_invalid_configuration(checkstyle_configs, use_spaces, indent_size):
    if (checkstyle_configs is 'google' and
            (not use_spaces or indent_size != 2)):
        raise ValueError('Google checkstyle config does not support '
                         'use_spaces=False or indent_size != 2')


def known_checkstyle_or_path(setting):
    if str(setting) in known_checkstyles.keys():
        return str(setting)
    else:
        return path(setting)


@linter(executable='java',
        normalize_column_numbers=True,
        remove_zero_numbers=True,
        output_format='regex',
        output_regex=r'\[(?P<severity>ERROR|WARN|INFO)\].*?'
                     r'(?P<line>\d+):?(?P<column>\d+)?. '
                     r'(?P<message>.*?) *\[(?P<origin>[a-zA-Z]+?)\]')
class CheckstyleBear:
    """
    Check Java code for possible style, semantic and design issues.

    For more information, consult
    <http://checkstyle.sourceforge.net/checks.html>.
    """

    LANGUAGES = {'Java'}
    REQUIREMENTS = {DistributionRequirement(apt_get='default-jre')}
    AUTHORS = {'The coala developers'}
    AUTHORS_EMAILS = {'coala-devel@googlegroups.com'}
    LICENSE = 'AGPL-3.0'
    CAN_DETECT = {'Formatting', 'Smell'}

    def setup_dependencies(self):
        version = _checkstyle_version
        type(self).checkstyle_jar_file = self.download_cached_file(
            'https://github.com/checkstyle/checkstyle/releases/download/'
            'checkstyle-%s/checkstyle-%s-all.jar' % (version, version),
            'checkstyle-6.19.jar')

    def create_arguments(
            self, filename, file, config_file,
            checkstyle_configs: known_checkstyle_or_path = 'google',
            use_spaces: bool = True,
            indent_size: int = 2,
            ):
        """
        :param checkstyle_configs:
            A file containing configs to use in ``checkstyle``. It can also
            have the special values:

            - google - Google's Java style. More info at
              <http://checkstyle.sourceforge.net/style_configs.html>.
            - sun - Sun's Java style. These are the same
              as the default Eclipse checks. More info at
              <http://checkstyle.sourceforge.net/style_configs.html>.
            - android-check-easy - The easy Android configs provided by the
              android-check eclipse plugin. More info at
              <https://github.com/noveogroup/android-check>.
            - android-check-hard - The hard Android confis provided by the
              android-check eclipse plugin. More info at
              <https://github.com/noveogroup/android-check>.
            - geosoft - The Java style followed by GeoSoft. More info at
              <http://geosoft.no/development/javastyle.html>
        :param use_spaces:
            If checkstyle_configs = Google, indentation checking using 2 spaces,
            according to https://google.github.io/styleguide/javaguide.html#s4.2-block-indentation,
            hence a 'True' value
        :param indent_size:
            If checkstyle_configs = Google, indentation checking using 2 spaces,
            according to https://google.github.io/styleguide/javaguide.html#s4.2-block-indentation
            
        """
        check_invalid_configuration(
            checkstyle_configs, use_spaces, indent_size)

        if checkstyle_configs in ('google', 'sun'):
            # Checkstyle included these two rulesets since version 6.2
            # Locate the file as an absolute resource into the checkstyle jar
            checkstyle_configs = '/%s_checks.xml' % checkstyle_configs
        elif checkstyle_configs in _online_styles:
            checkstyle_configs = self.download_cached_file(
                _online_styles[checkstyle_configs],
                checkstyle_configs + '.xml')

        return ('-jar', self.checkstyle_jar_file, '-c',
                checkstyle_configs, filename)
