"""A comparison template modeled on typical drag-and-drop editor exports:
a large reset/style block, and every product as a full nested section with repeated
inline styling and its own button. No cap on the loop."""
FONT = "font-family:'Helvetica Neue',Helvetica,Arial,Verdana,sans-serif;"
css_rules = []
for bp in (620, 600, 480, 420, 375):
    for k in range(18):
        css_rules.append(f".mcnBlock{k}_{bp}{{width:100%!important;max-width:100%!important;padding:0 18px!important;{FONT}font-size:16px!important;line-height:150%!important}}")
head = ("<!DOCTYPE html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width'>"
        "<style>" + "body,table,td,a{-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%}" * 12 +
        "".join(f"@media only screen and (max-width:{bp}px){{{''.join(r for r in css_rules if r.endswith('}') and f'_{bp}' in r)}}}" for bp in (620, 600, 480, 420, 375)) +
        "</style></head><body style='margin:0;padding:0'>")
wrap = lambda inner: ("<table role='presentation' border='0' cellpadding='0' cellspacing='0' width='100%' class='mcnBlock1' style='min-width:100%;border-collapse:collapse'><tbody class='mcnBlockOuter'><tr><td valign='top' class='mcnBlockInner' style='padding:9px'>"
                      "<!--[if mso]><table align='center' border='0' cellspacing='0' cellpadding='0' width='600' style='width:600px'><tr><td align='center' valign='top' width='600' style='width:600px'><![endif]-->"
                      f"<table role='presentation' align='left' border='0' cellpadding='0' cellspacing='0' width='100%' class='mcnBlockContentContainer' style='min-width:100%;border-collapse:collapse'><tbody><tr><td valign='top' class='mcnTextContent' style='padding:0 18px 9px;{FONT}color:#202020;font-size:16px;line-height:150%;text-align:left;word-break:break-word'>{inner}</td></tr></tbody></table>"
                      "<!--[if mso]></td></tr></table><![endif]--></td></tr></tbody></table>")
spacer = "<table role='presentation' border='0' cellpadding='0' cellspacing='0' width='100%' style='min-width:100%;border-collapse:collapse'><tbody><tr><td style='padding:18px 18px 0'><table border='0' cellpadding='0' cellspacing='0' width='100%' style='min-width:100%;border-top:1px solid #EAEAEA;border-collapse:collapse'><tbody><tr><td><span></span></td></tr></tbody></table></td></tr></tbody></table>"
item = ("{% for item in event.extra.line_items %}" +
        wrap(f"<table role='presentation' width='100%' style='border-collapse:collapse'><tr><td style='padding:0;{FONT}'><img src='{{{{ item.product.images.0.src }}}}' width='264' style='max-width:264px;padding-bottom:0;display:inline;vertical-align:bottom' alt=''></td></tr></table>") +
        wrap(f"<h3 style='display:block;margin:0;padding:0;color:#202020;{FONT}font-size:20px;font-style:normal;font-weight:bold;line-height:125%;letter-spacing:normal;text-align:left'>{{{{ item.product.title }}}}</h3><p style='margin:10px 0;padding:0;{FONT}color:#202020;font-size:16px;line-height:150%'>{{{{ item.product.variant.title }}}}</p><p style='margin:10px 0;padding:0;{FONT}color:#202020;font-size:16px;line-height:150%'>Quantity: {{{{ item.quantity }}}}</p><p style='margin:10px 0;padding:0;{FONT}color:#202020;font-size:16px;line-height:150%'>Price: ${{{{ item.line_price }}}}</p>") +
        wrap(f"<!--[if mso]><v:roundrect xmlns:v='urn:schemas-microsoft-com:vml' href='{{{{ event.extra.checkout_url }}}}' style='height:44px;v-text-anchor:middle;width:200px' arcsize='10%' stroke='f' fillcolor='#2BAADF'><w:anchorlock/><center style='color:#ffffff;{FONT}font-size:16px;font-weight:bold'>View item</center></v:roundrect><![endif]--><!--[if !mso]><!--><table border='0' cellpadding='0' cellspacing='0' class='mcnButtonContentContainer' style='border-collapse:separate!important;border-radius:3px;background-color:#2BAADF'><tbody><tr><td align='center' valign='middle' class='mcnButtonContent' style='{FONT}font-size:16px;padding:15px'><a class='mcnButton' title='View item' href='{{{{ event.extra.checkout_url }}}}' target='_blank' style='font-weight:bold;letter-spacing:normal;line-height:100%;text-align:center;text-decoration:none;color:#FFFFFF'>View item</a></td></tr></tbody></table><!--<![endif]-->") +
        spacer + "{% endfor %}")
body = (wrap("<h1 style='margin:0;font-size:26px'>Hi {{ person.first_name }}, you left something behind</h1>") + item +
        wrap("<p>Subtotal: ${{ event|lookup:'$value' }}</p>") + wrap("<a href='{{ event.extra.checkout_url }}'>Return to cart</a>") +
        wrap("<p style='font-size:12px'>Fernhill Goods, 12 Market Street, Portland, OR 97204<br>{% unsubscribe 'Unsubscribe' %}</p>") + "</body></html>")
open("src/naive_email.html", "w").write(head + body)
print("naive template bytes:", len(head + body))
