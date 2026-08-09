def conv(s):
    return s.replace(" ", "").translate(str.maketrans("UDLR", "^v<>"))

gp = "UURRR URDDD DDLLL LUUUU LLULD DDRRR RRRRD DDDLD DRLUU RUULD DUUUU RRRRR RDDDD DRDRU RULRR"
steam = "UURRR URDDD DDRLL ULDDD RDLDD DDDLD DRLUU RUULL DDUUU UUUUR RRRDR RR"
ours = "^^>>>^>vvvvv<<<<^^^^<<^<vvv>>>>>>>vvvv<vv><^^>^^<vv^^^^>>>>>>vvvvv>v>^>^<>>"

print("gp   ", len(conv(gp)), conv(gp))
print("steam", len(conv(steam)), conv(steam))
print("ours ", len(ours), ours)
print("ours==gp", ours == conv(gp))
print("ours==steam", ours == conv(steam))

# show first diff vs gp
a, b = ours, conv(gp)
for i, (x, y) in enumerate(zip(a, b)):
    if x != y:
        print("diff@", i, "ours", a[max(0,i-5):i+8], "gp", b[max(0,i-5):i+8])
        break
else:
    print("prefix equal, lens", len(a), len(b))
