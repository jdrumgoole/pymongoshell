def escape(s):
    return s.replace("<", "&" + "lt")


def header():
    return ("<!DOCTYPE html>\n"
            '<html lang="en">\n'
            "<head>\n"
            '   <meta charset="UTF-8">\n'
            '   <title>Invite to MongoDB Europe 2018</title>\n'
            '</head>\n')


def style():
    print("<style>\n",
          "pre {\n",
          '    font-family: "Courier", serif;\n',
          "}\n",
          "* {\n",
          '    font-family: "Arial", serif;\n',
          "}\n",
          ".button {\n",
          "   background-color: #4CAF50;\n",
          "   color: white;\n",
          "   padding: 15px 32px;\n",
          "   text-align: center;\n",
          "   border-radius: 12px;\n",
          "   text-decoration: none;\n",
          "   display: inline-block;\n",
          "   font-size: 16px;\n",
          "   margin: 4px 2px;\n",
          "   cursor: pointer;\n",
          "}\n",
          "</style>\n")


def body():
    print("\n",
          "<body>\n",
          "<h1>Invite to MongoDB Europe</h1>\n",
          "hi {},\n",
          "<p>\n",
          "Simplify application development. Standardize on MongoDB across a complete range of use cases, serving your users securely, wherever they are.\n",
          "</p>\n",
          "<p>\n",
          "Learn more at MongoDB Europe 2018.\n",
          "</p>\n",
          "<p>\n",
          "Talks include:\n",
          "</p>\n",
          "<ul>\n",
          "    <li>Tips and Tricks for Avoiding Common Query Pitfalls\n",
          "    <li>Workload Isolation: Are You Doing it Wrong?\n",
          "    <li>How and When to Use Multi-Document Distributed Transaction\n",
          "</ul>\n",
          "<p>\n",
          '<a href="http://mongodb.com" class="button">Save On Tickets</a>\n',
          "</p>\n",
          "<p>hear from</p>",
          "<ul>\n",
          "    <li>Dev Ittycheria, CEO of MongoDB\n",
          "    <li>Eliot Horowitz, CTO and Co-founder\n",
          "</ul>\n",
          "\n",
          "<p>\n",
          "    On Tuesday, 31st July, MongoDB Europe Super Early Bird ticket sales end.\n",
          "Beat the price rise - get your tickets now!\n",
          "</p>\n",
          "\n",
          "<p>\n",
          " Kind regards,\n",
          "</p>\n",
          "The MongoDB Team\n",
          "<h1>The code for this page</h1>\n",
          "</body>\n")


def pre():
    return "<pre>\n" + escape(open(__file__).read()) + "</pre>"

if __name__ == "__main__":
    print("<!DOCTYPE html>\n"
          '<html lang="en">\n')
    print(header())
    style()  # print(style())
    body()  # print(body())
    print(pre())
    print("</html")
