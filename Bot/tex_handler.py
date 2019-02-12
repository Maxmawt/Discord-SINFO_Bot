# created by Luis Tascon Gutierrez on Thursday, 12 february 2019
import os

LATEX_TEMPLATE = '../template.tex'


# Generate LaTeX locally.
def generate_image(my_latex, name):

    latex_file = name + '.tex'
    dvi_file = name + '.dvi'
    png_file = name + '1.png'

    with open(LATEX_TEMPLATE, 'r') as tex_template_file:
        tex_template = tex_template_file.read()

        with open(latex_file, 'w') as tex:
            background_colour = "36393E"
            text_colour = "DBDBDB"
            my_latex = tex_template.\
                replace('__DATA__', my_latex).\
                replace('__BGCOLOUR__', background_colour).\
                replace('__TEXTCOLOUR__', text_colour)

            tex.write(my_latex)
            tex.flush()
            tex.close()

    image_dpi = "200"
    latex_success = os.system('latex -quiet -interaction=nonstopmode ' + latex_file)
    print('Success = {}'.format(latex_success))
    if latex_success == 0:
        os.system('dvipng -q* -D {0} -T tight '.format(image_dpi) + dvi_file)
        return png_file
    else:
        return ''


# Removes the generated output files for a given name
def cleanup_output_files(outputnum):
    try:
        os.remove(outputnum + '.tex')
        os.remove(outputnum + '.dvi')
        os.remove(outputnum + '.aux')
        os.remove(outputnum + '.log')
        os.remove(outputnum + '1.png')
    except OSError:
        pass
