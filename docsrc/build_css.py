import sass
with open('_static/custom.css', 'w') as f:
    f.write(sass.compile(filename='_sass/modules.scss', include_paths='_sass', output_style='compressed'))
