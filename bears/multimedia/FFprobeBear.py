import json
from coalib.bearlib.abstractions.Linter import linter
from coalib.results.Result import Result


@linter(executable='ffprobe',
        output_format=None,
        prerequisite_check_command=('which', 'ffprobe'),
        prerequisite_check_fail_message='FFprobe (and thus probably FFmpeg) is'
                                        ' not installed. Refer '
        'https://ffmpeg.org/download.html for installation details.')
class FFprobeBear:
    """
    Analyze multimedia files for certain properties.

    At this point it only supports resolution checking for video files.

    For more information about the capabilities of FFprobe visit
    <https://ffmpeg.org/ffprobe.html>
    """
    AUTHORS = {'The coala developers'}
    AUTHORS_EMAILS = {'coala-devel@googlegroups.com'}
    LICENSE = 'AGPL-3.0'
    USE_RAW_FILES = True

    def check_stream(self, stream, width, height):
        result = {}
        if stream['width'] != int(width) or stream['height'] != int(height):
            result['message'] =\
                'The File has the wrong resolution: {}*{} instead of the ' \
                'wanted {}*{}.'.format(
                stream['width'], stream['height'], width, height)
        return result

    def process_output(self, output, filename, file,
                       video_width: int=1920, video_height: int=1080):
        output = json.loads(output)
        if output == {} or [1 for stream in output['streams'] if
                            stream['codec_type'] == 'video'] == []:
            yield Result.from_values(
                origin='{} ({})'.format(self.name, 'resolution check'),
                message='File Problem',
                additional_info='FFprobe either returned an empty json object '
                                'or there was no video stream in the file. '
                                'Both are signs for the file not being a video'
                                ' file.',
                file=filename
            )

        else:
            for stream in output['streams']:

                if stream['codec_type'] == 'video':
                    result = self.check_stream(
                        stream, video_width, video_height)

                    if result:

                        yield Result.from_values(
                            origin='{} ({})'.format(
                                self.name, 'resolution check'),
                            message=result['message'],
                            file=filename
                        )

    @staticmethod
    def create_arguments(filename, file, config_file):
        """
        Bear configuration arguments.
        """
        arguments = ('-v', 'quiet',
                     '-print_format', 'json',
                     '-show_format',
                     '-show_streams',
                     filename)
        return arguments
