import elevation
import PySimpleGUI as sg

font=(sg.DEFAULT_FONT, 16)

def clip(out_file, bounds):
    # Parse bounds into a tuple of floats
    clipped_data = elevation.clip(output=out_file, bounds=bounds)

    sg.popup('Clip successful!', font=font)



layout = [
    [sg.Text('Output file:', font=font),  sg.InputText(font=font), sg.FileSaveAs(font=font), sg.Text('Will be saved as: ".tif" file', font=font)],
    [sg.Text('Bounds', font=font)],
    [sg.Text('Minimum Latitude:', font=font), sg.InputText('12.35', font=font), sg.Text('Maximum Latitude:', font=font), sg.InputText('12.65', font=font)],
    [sg.Text('Minimum Longitude:', font=font), sg.InputText('41.8', font=font), sg.Text('Maximum Longitude:', font=font), sg.InputText('42', font=font)],
    [sg.Button('Clip', font=font)]
]

window = sg.Window('Elevation Clip', layout)

while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    if event == 'Clip':
        out_file = values[0]
        basename = '.'.join(values[0].split('.')[0:])
        ext = values[0].split('.')[-1].lower()
        if out_file != ext:
            out_file = basename + '.tif'
        else:
            out_file = out_file + '.tif'

        print(f'filename: {out_file}')
        print(f'basename: {basename}')

        try:
            min_lat = float(values[1])
            max_lat = float(values[2])
            min_lon = float(values[3])
            max_lon = float(values[4])
        except ValueError:
            sg.popup('ERROR: input was not a number!', font=font)
            continue
        if min_lat >= max_lat:
            sg.popup('ERROR: Minimum Latitude >= Maximum Latitude', font=font)
            continue
        if min_lon >= max_lon:
            sg.popup('ERROR: Minimum Longitude >= Maximum Longitude', font=font)
            continue
        for val in [min_lat, max_lat]:
            if val > 90.0 or val < -90.0:
                sg.popup('ERROR: Latitude was out of range!', font=font)
                continue
        for val in [min_lon, max_lon]:
            if val > 180.0 or val <= -180.0:
                sg.popup('ERROR: Longitude was out of range!', font=font)
                continue

        clip(out_file, (min_lat, min_lon, max_lat, max_lon))

window.close()
