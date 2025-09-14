def scrollbar(direction, base_color, color):
    style = f"""
    QScrollBar:{direction} {{
        border: none; 
        background-color: #{base_color}; 
        {'width' if direction == 'vertical' else 'height'}: 10px; 
        margin: 0px 0px 0px 0px; 
    }}
    
    QScrollBar::handle:{direction} {{
        background-color: #{color}; 
        border-radius: 5px; 
    }}
    
    QScrollBar::handle:{direction}:hover {{
        background-color: #999999; 
    }}
    
    QScrollBar::add-line:{direction}, QScrollBar::sub-line:{direction} {{
        border: none; 
        background: none; 
    }}
    
    QScrollBar::add-page:{direction}, QScrollBar::sub-page:{direction} {{
        background: none;
    }}
    """
    return style

def table(border, border_color, table_color, header_color, header_border, text_color):
    style = f''' 
    QTableWidget {{
        background-color: #{table_color}; 
        border: {border}px solid #{border_color}; 
        border-radius: 0px;
        text-align: center;
        color: #0055FF;
    }}



    QHeaderView::section {{
        background-color: #{header_color}; /* Background color */
        color: #{text_color}; /* Text color */
        border: 1px solid #{header_border}; 
        border-radius: 0px;
        font: Berlin Sans Fb; 
        font-size: 13px;
    }}
    
'''
    return style

def button(clolor):
    style = f"""
        QPushButton {{
            background-color: #00000000; /* Button Background Color */
            color: #{clolor}; /* Text Color */
            border: 2px solid #{clolor}; /* Border around the header */
            border-radius: 7px; /* Rounded Corners */
        }}

        QPushButton:hover {{
            background-color: #{clolor}; /* Red Background Color on Hover */
            color: white; /* Text Color */
        }}

        QPushButton:pressed {{
            background-color: #{clolor}; /* Even Darker Background Color when Pressed */
        }}
"""
    return style

# def main(color):
#     style = f"""
#             QMainWindow {{
#                 background-color: #{color}; /* Background color */
#                 color: #F6F6F6; /* Text color */
#             }}
#             QLineEdit {{
#                 background-color: #F2EFE5;
#                 border: 1px solid #cccccc; /* Light Gray Border */
#                 border-radius: 3px; /* Rounded Corners */
#             }}
#             QLineEdit:focus {{
#                 border-color: #007acc; /* Blue border color when focused */
#             }} 
#     """
#     return style

def groupBox(border, border_color, line_edit_color, border_lineEdit, textColor):
    style = f"""
            QGroupBox {{
                border: {border}px solid #{border_color}; /* Light Gray Border */
                border-radius: 10px; /* Rounded Corners */
                color: #F6F6F6;
                
            }}
            QLabel {{
                color: #{textColor};
                
            }}
            QGroupBox::title {{
                background-color: #EBD9B4;
                color: #333333; /* Dark Gray Text Color */
                border: 2px solid #cccccc; /* Dotted Border */
                border-radius: 5px;
            }}

            QLineEdit {{
                background-color: #{line_edit_color};
                border: 1px solid #{border_lineEdit}; /* Light Gray Border */
                border-radius: 3px; /* Rounded Corners */
            }}

            QLineEdit:focus {{
                border-color: #007acc; /* Blue border color when focused */
            }}
"""
    return style

def lineEdit(border, border_color, lineEditColor):
    style = f"""
        QLineEdit {{
            background-color: #{lineEditColor};
            border: {border}px solid #{border_color}; /* Light Gray Border */
            border-radius: 3px; /* Rounded Corners */
        }}

        QLineEdit:focus {{
            border-color: #007acc; /* Blue border color when focused */
        }}

    """
    return style