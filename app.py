from flask import Flask, render_template, request
import pandas as pd
import io

app = Flask(__name__)

def read_file(file):
    file_type = file.filename.split('.')[-1].lower()
    if file_type == 'csv':
        return pd.read_csv(io.StringIO(file.read().decode('utf-8')))
    elif file_type == 'txt':
        return pd.read_csv(io.StringIO(file.read().decode('utf-8')), delimiter='\t')
    elif file_type in ['xls', 'xlsx']:
        return pd.read_excel(file)
    else:
        raise ValueError("Unsupported file type")

def compare_tables(df1, df2):
    # Find differences between two dataframes
    diff = pd.concat([df1, df2]).drop_duplicates(keep=False)
    
    # Number of rows and columns
    info1 = (df1.shape[0], df1.shape[1])
    info2 = (df2.shape[0], df2.shape[1])
    
    # Compare column headers
    headers1 = set(df1.columns)
    headers2 = set(df2.columns)
    headers_diff = {
        "Only in Table 1": headers1 - headers2,
        "Only in Table 2": headers2 - headers1
    }
    
    return diff, info1, info2, headers_diff

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file1 = request.files['file1']
        file2 = request.files['file2']
        
        if file1 and file2:
            try:
                df1 = read_file(file1)
                df2 = read_file(file2)
                
                comparison_result, info1, info2, headers_diff = compare_tables(df1, df2)
                return render_template(
                    'result.html',
                    tables=[df1.to_html(classes='table'), df2.to_html(classes='table'), comparison_result.to_html(classes='table')],
                    info1=info1,
                    info2=info2,
                    headers_diff=headers_diff
                )
            except ValueError as e:
                return str(e)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
