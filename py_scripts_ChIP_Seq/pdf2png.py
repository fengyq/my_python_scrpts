def pdf2png(pdf, out_dir):
    prefix = os.path.join(out_dir,
                          os.path.basename(strip_ext(pdf)))
    png = '{}.png'.format(prefix)

    cmd = 'gs -dFirstPage=1 -dLastPage=1 -dTextAlphaBits=4 '
    cmd += '-dGraphicsAlphaBits=4 -r110x110 -dUseCropBox -dQUIET '
    cmd += '-dSAFER -dBATCH -dNOPAUSE -dNOPROMPT -sDEVICE=png16m '
    cmd += '-sOutputFile={} -r144 {}'
    cmd = cmd.format(
        png,
        pdf)
    run_shell_cmd(cmd)
    return png
    
