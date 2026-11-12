import ast
import json
import os
import sys
import math
import time
import random
import colorsys
import subprocess
from datetime import datetime

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, simpledialog
except ImportError:
    print("Máy này chưa cài tkinter nên không mở được giao diện đồ họa.")
    sys.exit(1)

THU_MUC = os.path.dirname(os.path.abspath(__file__))
THU_MUC_DL = os.path.join(THU_MUC, "du_lieu")
FILE_KHO = os.path.join(THU_MUC_DL, "kho_hang.py")
FILE_MUA = os.path.join(THU_MUC_DL, "lich_su_mua.py")
FILE_KET = os.path.join(THU_MUC_DL, "ket_tien.py")
FILE_JSON_CU = os.path.join(THU_MUC, "du_lieu_may_ban_hang.json")
MAT_KHAU_ADMIN = "meobeo"
NGUONG_SAP_HET = 3
CHU_KY_NHAP_HANG = 40
DON_VI_TIEN = 1000
TY_LE_GIA_VON = 0.65
MENH_GIA_NHAN = [1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000, 500000]
MENH_GIA_THOI = [50000, 20000, 10000, 5000, 2000, 1000]
MENH_GIA_SIM = [1000, 2000, 5000, 10000, 20000, 50000]
MENH_KET = sorted(MENH_GIA_NHAN, reverse=True)
KET_BAN_DAU = {50000: 2, 20000: 5, 10000: 10, 5000: 20, 2000: 20, 1000: 20}

NEN_TOI = "#0b0620"
CARD_BG = "#160f38"
CHU = "#efe6ff"
CHU_PHU = "#b9a8f0"
VANG = "#ffd76a"
TIM = "#7c4dff"
TIM_SANG = "#9d7bff"
HONG = "#ff6bd6"
XANH_LA = "#8be9c3"
CAM = "#ffb347"
DO_NHAT = "#ff8fa3"

CW = 270
CH = 205
GAP = 24
SO_DAI = 48
SO_SAO = 80

CAU_DAN = [
    "Mỗi món đồ là một lời tiên tri - chạm vào để mở khóa vận may",
    "Vũ trụ thì thầm: hôm nay bạn xứng đáng được thưởng thức",
    "Một lần chạm - một điều bất ngờ đang chờ bạn",
    "Ánh sao đã chọn sẵn một món dành riêng cho bạn",
    "Đừng để định mệnh chờ lâu - hãy chọn ngay ô của bạn",
]

LOI_TIEN_TRI = [
    "Ngôi sao dẫn lối: hôm nay là ngày may mắn của bạn!",
    "Năng lượng mới đang chảy về phía bạn, hãy tận hưởng nhé.",
    "Một niềm vui nhỏ vừa được mở khóa - còn nhiều điều bất ngờ phía trước.",
    "Vận may mỉm cười với người biết tự thưởng cho mình.",
    "Chúc bạn một ngày thật nhiều cảm hứng và thật nhiều niềm vui!",
]


def hls_hex(h, l, s):
    r, g, b = colorsys.hls_to_rgb(h % 1.0, l, s)
    return "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))


def tien(so):
    return f"{so:,}".replace(",", ".") + "đ"


def tien_dau(so):
    return ("+" if so >= 0 else "-") + tien(abs(so))


def bay_gio():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def gia_von_mac_dinh(gia):
    return max(DON_VI_TIEN, int(gia * TY_LE_GIA_VON / DON_VI_TIEN + 0.5) * DON_VI_TIEN)


def du_lieu_mac_dinh():
    return {
        "slots": {
            "A1": {"ten": "Nước suối", "gia": 5000, "gia_von": 3000, "so_luong": 10, "suc_chua": 15},
            "A2": {"ten": "Coca Cola", "gia": 10000, "gia_von": 7000, "so_luong": 8, "suc_chua": 12},
            "A3": {"ten": "Trà xanh 0 độ", "gia": 12000, "gia_von": 8000, "so_luong": 6, "suc_chua": 12},
            "B1": {"ten": "Snack khoai tây", "gia": 8000, "gia_von": 5000, "so_luong": 12, "suc_chua": 15},
            "B2": {"ten": "Bánh quy", "gia": 15000, "gia_von": 10000, "so_luong": 2, "suc_chua": 10},
            "B3": {"ten": "Kẹo cao su", "gia": 3000, "gia_von": 2000, "so_luong": 20, "suc_chua": 25},
        },
        "gd_that": [],
        "gd_gia_lap": [],
        "gd_cu": [],
        "nhap_hang": [],
        "ket": {m: KET_BAN_DAU.get(m, 0) for m in MENH_KET},
        "ket_ban_dau": {m: KET_BAN_DAU.get(m, 0) for m in MENH_KET},
        "khoi_dau": bay_gio(),
    }


def doc_file_py(duong_dan):
    ket_qua = {}
    with open(duong_dan, "r", encoding="utf-8") as f:
        cay = ast.parse(f.read())
    for nut in cay.body:
        if isinstance(nut, ast.Assign) and len(nut.targets) == 1 and isinstance(nut.targets[0], ast.Name):
            ket_qua[nut.targets[0].id] = ast.literal_eval(nut.value)
    return ket_qua


def dinh_dang_gia_tri(ten, v):
    return f"{ten} = {v!r}\n"


def dinh_dang_dict(ten, d):
    if not d:
        return f"{ten} = {{}}\n"
    dong = [f"{ten} = {{"]
    for k, v in d.items():
        dong.append(f"    {k!r}: {v!r},")
    dong.append("}")
    return "\n".join(dong) + "\n"


def dinh_dang_list(ten, ds):
    if not ds:
        return f"{ten} = []\n"
    dong = [f"{ten} = ["]
    for v in ds:
        dong.append(f"    {v!r},")
    dong.append("]")
    return "\n".join(dong) + "\n"


def ghi_file_py(duong_dan, tieu_de, phan):
    noi_dung = f'"""{tieu_de}"""\n\nCAP_NHAT = {bay_gio()!r}\n\n' + "\n".join(phan)
    tam = duong_dan + ".tmp"
    with open(tam, "w", encoding="utf-8") as f:
        f.write(noi_dung)
    os.replace(tam, duong_dan)


def sap_xep_ket(ket):
    return dict(sorted(ket.items(), reverse=True))


def chuan_hoa(dl):
    for s in dl["slots"].values():
        if "gia_von" not in s:
            s["gia_von"] = gia_von_mac_dinh(s["gia"])
    for khoa in ("ket", "ket_ban_dau"):
        for m in MENH_KET:
            dl[khoa].setdefault(m, 0)


def tai_du_lieu():
    dl = du_lieu_mac_dinh()
    da_doc = False
    try:
        if os.path.exists(FILE_KHO):
            kho = doc_file_py(FILE_KHO)
            dl["slots"] = kho.get("SLOTS", dl["slots"])
            dl["nhap_hang"] = kho.get("LICH_SU_NHAP", [])
            da_doc = True
        if os.path.exists(FILE_MUA):
            mua = doc_file_py(FILE_MUA)
            dl["gd_that"] = mua.get("GIAO_DICH_THAT", [])
            dl["gd_gia_lap"] = mua.get("GIAO_DICH_GIA_LAP", [])
            dl["gd_cu"] = mua.get("GIAO_DICH_CU", []) + mua.get("GIAO_DICH", [])
            da_doc = True
        if os.path.exists(FILE_KET):
            ket = doc_file_py(FILE_KET)
            if "KET" in ket and "KET_BAN_DAU" in ket and "KHOI_DAU" in ket:
                dl["ket"] = ket["KET"]
                dl["ket_ban_dau"] = ket["KET_BAN_DAU"]
                dl["khoi_dau"] = ket["KHOI_DAU"]
    except (OSError, SyntaxError, ValueError):
        print("Không đọc được file dữ liệu trong thư mục du_lieu, dùng dữ liệu mặc định.")
    if not da_doc and os.path.exists(FILE_JSON_CU):
        try:
            with open(FILE_JSON_CU, "r", encoding="utf-8") as f:
                cu = json.load(f)
            dl["slots"] = cu["slots"]
            dl["gd_cu"] = cu.get("giao_dich", [])
            dl["nhap_hang"] = cu.get("nhap_hang", [])
        except (OSError, ValueError, KeyError):
            pass
    chuan_hoa(dl)
    return dl


TRANG_THAI = {"loi": ""}


def luu_du_lieu(dl):
    try:
        os.makedirs(THU_MUC_DL, exist_ok=True)
        ghi_file_py(FILE_KHO, "Du lieu kho hang cua may ban hang (tu dong cap nhat)", [
            dinh_dang_dict("SLOTS", dl["slots"]),
            dinh_dang_list("LICH_SU_NHAP", dl["nhap_hang"]),
        ])
        phan_mua = [
            dinh_dang_list("GIAO_DICH_THAT", dl["gd_that"]),
            dinh_dang_list("GIAO_DICH_GIA_LAP", dl["gd_gia_lap"]),
        ]
        if dl["gd_cu"]:
            phan_mua.append(dinh_dang_list("GIAO_DICH_CU", dl["gd_cu"]))
        ghi_file_py(FILE_MUA, "Lich su mua hang: khach that va khach gia lap ghi rieng (tu dong cap nhat)", phan_mua)
        ghi_file_py(FILE_KET, "Ket tien cua may ban hang (tu dong cap nhat)", [
            dinh_dang_gia_tri("KHOI_DAU", dl["khoi_dau"]),
            dinh_dang_dict("KET_BAN_DAU", sap_xep_ket(dl["ket_ban_dau"])),
            dinh_dang_dict("KET", sap_xep_ket(dl["ket"])),
        ])
        TRANG_THAI["loi"] = ""
    except OSError as e:
        TRANG_THAI["loi"] = str(e.strerror or e)


def mo_bang_trinh_soan_thao(duong_dan):
    if sys.platform.startswith("win"):
        subprocess.Popen(["notepad.exe", duong_dan])
    elif sys.platform == "darwin":
        subprocess.Popen(["open", "-t", duong_dan])
    else:
        subprocess.Popen(["xdg-open", duong_dan])


def mo_thu_muc(duong_dan):
    if sys.platform.startswith("win"):
        os.startfile(duong_dan)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", duong_dan])
    else:
        subprocess.Popen(["xdg-open", duong_dan])


def tong_ket(ket):
    return sum(m * n for m, n in ket.items())


def chuoi_to(to):
    return ", ".join(f"{n} x {tien(m)}" for m, n in sorted(to.items(), reverse=True))


def tim_to_tien(ket, so_tien, menh_cho_phep):
    if so_tien < 0 or so_tien % DON_VI_TIEN:
        return None
    if so_tien == 0:
        return {}
    if so_tien > sum(m * ket.get(m, 0) for m in menh_cho_phep):
        return None
    dich = so_tien // DON_VI_TIEN
    vat = []
    for menh in sorted(menh_cho_phep, reverse=True):
        con = ket.get(menh, 0)
        k = 1
        while con > 0:
            lay = min(k, con)
            vat.append((menh, lay, menh * lay // DON_VI_TIEN))
            con -= lay
            k *= 2
    vo_cung = 10 ** 9
    dp = [vo_cung] * (dich + 1)
    dp[0] = 0
    dau_vet = []
    for menh, lay, w in vat:
        moi = dp[:]
        dung = [False] * (dich + 1)
        for a in range(w, dich + 1):
            if dp[a - w] + lay < moi[a]:
                moi[a] = dp[a - w] + lay
                dung[a] = True
        dp = moi
        dau_vet.append(dung)
    if dp[dich] >= vo_cung:
        return None
    kq = {}
    a = dich
    for i in range(len(vat) - 1, -1, -1):
        if dau_vet[i][a]:
            menh, lay, w = vat[i]
            kq[menh] = kq.get(menh, 0) + lay
            a -= w
    return kq


def co_the_nhan_to(dl, gia, da_nap, menh):
    tong = da_nap + menh
    if tong < gia:
        return True
    return tim_to_tien(dl["ket"], tong - gia, MENH_GIA_THOI) is not None


def ban_hang(dl, ma, so_luong, to_khach, nguon):
    s = dl["slots"].get(ma)
    if s is None or s["so_luong"] < so_luong:
        return {"ok": False, "ly_do": "het_hang"}
    doanh_thu = s["gia"] * so_luong
    tien_nhan = sum(m * n for m, n in to_khach.items())
    if tien_nhan < doanh_thu:
        return {"ok": False, "ly_do": "thieu_tien"}
    thoi = tien_nhan - doanh_thu
    to_thoi = tim_to_tien(dl["ket"], thoi, MENH_GIA_THOI)
    if to_thoi is None:
        return {"ok": False, "ly_do": "khong_thoi_duoc", "thoi": thoi}
    for m, n in to_thoi.items():
        dl["ket"][m] -= n
    for m, n in to_khach.items():
        dl["ket"][m] = dl["ket"].get(m, 0) + n
    s["so_luong"] -= so_luong
    that = nguon == "that"
    ds = dl["gd_that"] if that else dl["gd_gia_lap"]
    gd = {
        "ma_gd": ("GD" if that else "GL") + f"{len(ds) + 1:04d}",
        "thoi_gian": bay_gio(),
        "slot": ma,
        "ten": s["ten"],
        "so_luong": so_luong,
        "don_gia": s["gia"],
        "gia_von": s["gia_von"],
        "tien_nhan": tien_nhan,
        "tien_thoi": thoi,
        "doanh_thu": doanh_thu,
    }
    ds.append(gd)
    return {"ok": True, "gd": gd, "to_thoi": to_thoi}


def nhap_hang_tra_tien(dl, ma, so, nguon, cho_giam):
    s = dl["slots"][ma]
    so = min(so, s["suc_chua"] - s["so_luong"])
    don_gia = s["gia_von"]
    if so <= 0:
        return {"ok": False, "can": 0, "ket": tong_ket(dl["ket"])}
    q = so
    to = None
    while q > 0:
        to = tim_to_tien(dl["ket"], q * don_gia, MENH_KET)
        if to is not None or not cho_giam:
            break
        q -= 1
    if q <= 0 or to is None:
        return {"ok": False, "can": so * don_gia, "ket": tong_ket(dl["ket"])}
    for m, n in to.items():
        dl["ket"][m] -= n
    s["so_luong"] += q
    dl["nhap_hang"].append({
        "thoi_gian": bay_gio(),
        "slot": ma,
        "ten": s["ten"],
        "so_luong": q,
        "ton_sau": s["so_luong"],
        "nguon": nguon,
        "don_gia_von": don_gia,
        "chi_phi": q * don_gia,
    })
    return {"ok": True, "so": q, "chi_phi": q * don_gia, "yeu_cau": so}


def chon_menh_gia_sim(doanh_thu):
    ung_vien = [m for m in MENH_GIA_SIM if -(-doanh_thu // m) <= 3]
    return random.choice(ung_vien) if ung_vien else max(MENH_GIA_SIM)


def tat_ca_gd(dl):
    return dl["gd_that"] + dl["gd_gia_lap"]


def tinh_lai_lo(dl):
    def tong_ban(ds):
        doanh_thu = sum(g["doanh_thu"] for g in ds)
        gia_von = sum(g.get("gia_von", 0) * g["so_luong"] for g in ds)
        return {"so_gd": len(ds), "so_sp": sum(g["so_luong"] for g in ds),
                "doanh_thu": doanh_thu, "gia_von": gia_von, "lai_gop": doanh_thu - gia_von}

    def tong_nhap(nguon):
        ds = [n for n in dl["nhap_hang"] if "chi_phi" in n and (nguon is None or n.get("nguon") == nguon)]
        return {"so_lan": len(ds), "so_sp": sum(n["so_luong"] for n in ds), "chi_phi": sum(n["chi_phi"] for n in ds)}

    ban = tong_ban(tat_ca_gd(dl))
    return {
        "that": tong_ban(dl["gd_that"]),
        "gia_lap": tong_ban(dl["gd_gia_lap"]),
        "ban": ban,
        "nhap_tu_dong": tong_nhap("Tự động"),
        "nhap_quan_tri": tong_nhap("Quản trị"),
        "nhap": tong_nhap(None),
        "ket_ban_dau": tong_ket(dl["ket_ban_dau"]),
        "ket_hien_tai": tong_ket(dl["ket"]),
        "ton_gia_tri_von": sum(s["gia_von"] * s["so_luong"] for s in dl["slots"].values()),
        "lai": ban["lai_gop"],
    }


def so_quy(dl):
    su_kien = []
    for g in dl["gd_that"]:
        su_kien.append((g["thoi_gian"], 0, "Bán - khách thật",
                        f"{g['so_luong']} x {g['ten']} (Ô {g['slot']})", g["doanh_thu"]))
    for g in dl["gd_gia_lap"]:
        su_kien.append((g["thoi_gian"], 1, "Bán - giả lập",
                        f"{g['so_luong']} x {g['ten']} (Ô {g['slot']})", g["doanh_thu"]))
    for n in dl["nhap_hang"]:
        if "chi_phi" in n:
            su_kien.append((n["thoi_gian"], 2, "Nhập hàng - " + str(n.get("nguon", "")).lower(),
                            f"{n['so_luong']} x {n['ten']} (Ô {n['slot']})", -n["chi_phi"]))
    su_kien.sort(key=lambda x: (x[0], x[1]))
    so_du = tong_ket(dl["ket_ban_dau"])
    kq = []
    for tg, _, loai, noi_dung, so_tien in su_kien:
        so_du += so_tien
        kq.append((tg, loai, noi_dung, so_tien, so_du))
    return kq


def thoi_gian_hoat_dong(khoi_dau):
    try:
        bd = datetime.strptime(khoi_dau, "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return "không rõ"
    giay = max(0, int((datetime.now() - bd).total_seconds()))
    ngay, du = divmod(giay, 86400)
    gio, du = divmod(du, 3600)
    return f"{ngay} ngày {gio} giờ {du // 60} phút"


def van_ban_lai_lo(dl):
    kq = tinh_lai_lo(dl)
    dong = ["=== TỔNG HỢP LÃI / LỖ ==="]
    dong.append(f"Bắt đầu tính từ    : {dl['khoi_dau']}  (lần chạy đầu tiên trên máy)")
    dong.append(f"Cập nhật lúc       : {bay_gio()}")
    dong.append(f"Thời gian hoạt động: {thoi_gian_hoat_dong(dl['khoi_dau'])}")
    dong.append("")
    dong.append("--- BÁN HÀNG ---")
    dong.append(f"{'':<16}{'Số GD':>7}{'Số SP':>7}{'Doanh thu':>14}{'Giá vốn':>14}{'Lãi gộp':>14}")
    for ten, v in (("Khách thật", kq["that"]), ("Khách giả lập", kq["gia_lap"]), ("Tổng", kq["ban"])):
        dong.append(f"{ten:<16}{v['so_gd']:>7}{v['so_sp']:>7}{tien(v['doanh_thu']):>14}"
                    f"{tien(v['gia_von']):>14}{tien(v['lai_gop']):>14}")
    dong.append("")
    dong.append("--- NHẬP HÀNG (đã trừ vào két) ---")
    dong.append(f"{'':<16}{'Số lần':>7}{'Số SP':>7}{'Chi phí':>14}")
    for ten, v in (("Tự động", kq["nhap_tu_dong"]), ("Quản trị", kq["nhap_quan_tri"]), ("Tổng", kq["nhap"])):
        dong.append(f"{ten:<16}{v['so_lan']:>7}{v['so_sp']:>7}{tien(v['chi_phi']):>14}")
    dong.append("")
    dong.append("--- KẾT QUẢ ---")
    dong.append(f"Lãi gộp (doanh thu - giá vốn hàng đã bán): {tien_dau(kq['lai'])}")
    dong.append(f"Tiền két ban đầu                         : {tien(kq['ket_ban_dau'])}")
    dong.append(f"Tiền két hiện tại                        : {tien(kq['ket_hien_tai'])}")
    dong.append(f"Chênh lệch két (thu bán - chi nhập hàng) : {tien_dau(kq['ket_hien_tai'] - kq['ket_ban_dau'])}")
    dong.append(f"Giá trị hàng tồn (theo giá vốn)          : {tien(kq['ton_gia_tri_von'])}")
    dong.append("(Chi nhập hàng làm giảm két nhưng tăng giá trị hàng tồn nên không phải khoản lỗ)")
    dong.append("")
    if kq["lai"] > 0:
        dong.append(f"KẾT LUẬN: LÃI {tien(kq['lai'])}")
    elif kq["lai"] < 0:
        dong.append(f"KẾT LUẬN: LỖ {tien(-kq['lai'])}")
    else:
        dong.append("KẾT LUẬN: HÒA VỐN (chưa có lãi)")
    return "\n".join(dong)


def trang_thai_slot(s):
    if s["so_luong"] == 0:
        return "HẾT HÀNG"
    if s["so_luong"] <= NGUONG_SAP_HET:
        return "SẮP HẾT"
    return "Còn hàng"


def tao_nut(parent, text, cmd, bg=TIM, size=11, state="normal"):
    return tk.Button(
        parent, text=text, command=cmd, bg=bg, fg="white",
        activebackground=TIM_SANG, activeforeground="white",
        disabledforeground="#8a7fb5", relief="flat", bd=0,
        padx=12, pady=6, font=("Segoe UI", size, "bold"),
        cursor="hand2", state=state,
    )


def tao_tree(parent, cot):
    khung = tk.Frame(parent, bg=NEN_TOI)
    tree = ttk.Treeview(khung, columns=[c[0] for c in cot], show="headings", selectmode="browse")
    for ten, nhan, rong, can in cot:
        tree.heading(ten, text=nhan)
        tree.column(ten, width=rong, anchor=can)
    sb = ttk.Scrollbar(khung, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=sb.set)
    tree.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")
    return khung, tree


class QuanTri:
    def __init__(self, app):
        self.app = app
        self.dl = app.dl
        self.win = tk.Toplevel(app.root)
        self.win.title("Quản trị viên - Máy Bán Hàng Huyền Bí")
        self.win.geometry("1100x720")
        self.win.configure(bg=NEN_TOI)
        self.dung_style()
        self.sim_bat = True
        self.sim_pha = "cho"
        self.sim_han = time.time() + random.uniform(1, 10)
        self.sim_job = None
        self.so_khach = 0
        thanh_sim = tk.Frame(self.win, bg=CARD_BG)
        thanh_sim.pack(fill="x", padx=10, pady=(10, 0))
        self.nut_sim = tao_nut(thanh_sim, "⏸ Tạm dừng khách giả lập", self.bat_tat_sim, size=10)
        self.nut_sim.pack(side="left", padx=8, pady=8)
        tao_nut(thanh_sim, "Thư mục dữ liệu", self.mo_thu_muc_dl, bg="#3a2a7a", size=9).pack(side="right", padx=4)
        tao_nut(thanh_sim, "Xem ket_tien.py", lambda: self.mo_file_dl(FILE_KET), bg="#3a2a7a", size=9).pack(side="right", padx=4)
        tao_nut(thanh_sim, "Xem lich_su_mua.py", lambda: self.mo_file_dl(FILE_MUA), bg="#3a2a7a", size=9).pack(side="right", padx=4)
        tao_nut(thanh_sim, "Xem kho_hang.py", lambda: self.mo_file_dl(FILE_KHO), bg="#3a2a7a", size=9).pack(side="right", padx=4)
        cot_chu = tk.Frame(thanh_sim, bg=CARD_BG)
        cot_chu.pack(side="left", fill="x", expand=True, padx=6)
        self.lbl_sim = tk.Label(cot_chu, text="", bg=CARD_BG, fg=XANH_LA, font=("Segoe UI", 10, "bold"), anchor="w")
        self.lbl_sim.pack(fill="x")
        self.lbl_su_kien = tk.Label(cot_chu, text="Chưa có khách nào.", bg=CARD_BG, fg=CHU_PHU,
                                    font=("Segoe UI", 10), anchor="w", justify="left", wraplength=620)
        self.lbl_su_kien.pack(fill="x")
        self.lbl_nhap = tk.Label(cot_chu, text="", bg=CARD_BG, fg=HONG, font=("Segoe UI", 10, "bold"), anchor="w")
        self.lbl_nhap.pack(fill="x")
        self.lbl_tin_nhap = tk.Label(cot_chu, text="", bg=CARD_BG, fg=HONG, font=("Segoe UI", 10, "bold"),
                                     anchor="w", justify="left", wraplength=620)
        self.lbl_tin_nhap.pack(fill="x")
        self.tabs = ttk.Notebook(self.win)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=10)
        self.tab_kho = tk.Frame(self.tabs, bg=NEN_TOI)
        self.tab_ket = tk.Frame(self.tabs, bg=NEN_TOI)
        self.tab_gd = tk.Frame(self.tabs, bg=NEN_TOI)
        self.tab_nhap = tk.Frame(self.tabs, bg=NEN_TOI)
        self.tab_lai = tk.Frame(self.tabs, bg=NEN_TOI)
        self.tab_quy = tk.Frame(self.tabs, bg=NEN_TOI)
        self.tab_bc = tk.Frame(self.tabs, bg=NEN_TOI)
        self.tabs.add(self.tab_kho, text="  Tồn kho & nhập hàng  ")
        self.tabs.add(self.tab_ket, text="  Két tiền  ")
        self.tabs.add(self.tab_gd, text="  Lịch sử giao dịch  ")
        self.tabs.add(self.tab_nhap, text="  Lịch sử nhập hàng  ")
        self.tabs.add(self.tab_lai, text="  Lãi / lỗ  ")
        self.tabs.add(self.tab_quy, text="  Sổ thu chi  ")
        self.tabs.add(self.tab_bc, text="  Doanh thu & báo cáo  ")
        self.xay_tab_kho()
        self.xay_tab_ket()
        self.xay_tab_gd()
        self.xay_tab_nhap()
        self.xay_tab_lai()
        self.xay_tab_quy()
        self.xay_tab_bao_cao()
        self.lam_moi()
        self.win.protocol("WM_DELETE_WINDOW", self.dong)
        self.sim_tick()

    def mo_file_dl(self, duong_dan):
        luu_du_lieu(self.dl)
        if not os.path.exists(duong_dan):
            messagebox.showerror("Không tìm thấy file",
                                 f"Chưa tạo được file:\n{duong_dan}\n\nLý do: {TRANG_THAI['loi'] or 'không rõ'}",
                                 parent=self.win)
            return
        try:
            mo_bang_trinh_soan_thao(duong_dan)
        except OSError as e:
            messagebox.showerror("Không mở được", f"{e}\n\nFile nằm tại:\n{duong_dan}", parent=self.win)

    def mo_thu_muc_dl(self):
        luu_du_lieu(self.dl)
        if not os.path.isdir(THU_MUC_DL):
            messagebox.showerror("Không tìm thấy thư mục",
                                 f"Chưa tạo được thư mục:\n{THU_MUC_DL}\n\nLý do: {TRANG_THAI['loi'] or 'không rõ'}",
                                 parent=self.win)
            return
        try:
            mo_thu_muc(THU_MUC_DL)
        except OSError as e:
            messagebox.showerror("Không mở được", f"{e}\n\nThư mục nằm tại:\n{THU_MUC_DL}", parent=self.win)

    def dong(self):
        if self.sim_job is not None:
            try:
                self.win.after_cancel(self.sim_job)
            except tk.TclError:
                pass
            self.sim_job = None
        self.win.destroy()

    def bat_tat_sim(self):
        self.sim_bat = not self.sim_bat
        if self.sim_bat:
            self.sim_pha = "cho"
            self.sim_han = time.time() + random.uniform(1, 10)
            self.nut_sim.config(text="⏸ Tạm dừng khách giả lập")
        else:
            self.nut_sim.config(text="▶ Bật khách giả lập")

    def sim_tick(self):
        if not self.win.winfo_exists():
            return
        self.lbl_nhap.config(text=f"▣ Hàng mới tự động về sau: {self.app.nhap_con_lai():.0f}s")
        if self.sim_bat:
            con = self.sim_han - time.time()
            if con <= 0:
                if self.sim_pha == "cho":
                    self.sim_mua()
                    self.sim_pha = "nghi"
                    self.sim_han = time.time() + 5
                else:
                    self.sim_pha = "cho"
                    self.sim_han = time.time() + random.uniform(1, 10)
                con = self.sim_han - time.time()
            if self.sim_pha == "cho":
                self.lbl_sim.config(text=f"● Đang chờ khách tiếp theo... ({max(0, con):.0f}s)", fg=XANH_LA)
            else:
                self.lbl_sim.config(text=f"● Nghỉ giữa hai khách... ({max(0, con):.0f}s)", fg=CAM)
        else:
            self.lbl_sim.config(text="○ Giả lập khách đang tắt", fg=CHU_PHU)
        self.sim_job = self.win.after(250, self.sim_tick)

    def sim_mua(self):
        slots = self.dl["slots"]
        con_hang = [m for m, s in slots.items() if s["so_luong"] > 0]
        if not con_hang:
            self.lbl_su_kien.config(text="Có khách ghé nhưng máy đã hết sạch hàng - cần nhập hàng!", fg=CAM)
            return
        mua = {}
        for _ in range(random.randint(1, 4)):
            cho = [m for m in con_hang if slots[m]["so_luong"] - mua.get(m, 0) > 0]
            if not cho:
                break
            m = random.choice(cho)
            mua[m] = mua.get(m, 0) + 1
        self.so_khach += 1
        tong_don = 0
        mo_ta = []
        tu_choi = []
        for m, q in mua.items():
            s = slots[m]
            doanh_thu = s["gia"] * q
            menh = chon_menh_gia_sim(doanh_thu)
            so_to = -(-doanh_thu // menh)
            kq = ban_hang(self.dl, m, q, {menh: so_to}, "gia_lap")
            ten = f"{q} x {s['ten']} ({m})"
            if kq["ok"]:
                tong_don += doanh_thu
                mo_ta.append(ten)
            elif kq["ly_do"] == "khong_thoi_duoc":
                tu_choi.append(f"{ten}: bỏ {so_to} tờ {tien(menh)}, máy không đủ tiền thối {tien(kq['thoi'])} nên trả lại khách")
            else:
                tu_choi.append(f"{ten}: hết hàng")
        luu_du_lieu(self.dl)
        self.lam_moi()
        text = f"Khách #{self.so_khach} ({bay_gio()[11:]}): "
        if mo_ta:
            text += ", ".join(mo_ta) + f"  ->  {tien(tong_don)}"
        if tu_choi:
            text += ("   |   " if mo_ta else "") + "⚠ KHÔNG ĐỦ TIỀN THỐI: " + "; ".join(tu_choi)
        self.lbl_su_kien.config(text=text, fg=CAM if tu_choi else VANG)

    def dung_style(self):
        st = ttk.Style(self.win)
        st.theme_use("clam")
        st.configure("Treeview", background=CARD_BG, fieldbackground=CARD_BG, foreground=CHU,
                     rowheight=28, borderwidth=0, font=("Segoe UI", 10))
        st.configure("Treeview.Heading", background="#3a2a7a", foreground="white",
                     font=("Segoe UI", 10, "bold"), relief="flat")
        st.map("Treeview", background=[("selected", TIM)], foreground=[("selected", "white")])
        st.map("Treeview.Heading", background=[("active", TIM)])
        st.configure("TNotebook", background=NEN_TOI, borderwidth=0)
        st.configure("TNotebook.Tab", background="#2a1d5e", foreground=CHU,
                     padding=(12, 8), font=("Segoe UI", 10, "bold"))
        st.map("TNotebook.Tab", background=[("selected", TIM)], foreground=[("selected", "white")])
        st.configure("Vertical.TScrollbar", background="#3a2a7a", troughcolor=CARD_BG, borderwidth=0)

    def xay_tab_kho(self):
        self.lbl_canh_bao = tk.Label(self.tab_kho, text="", bg=NEN_TOI, fg=CAM,
                                     font=("Segoe UI", 11, "bold"), wraplength=1000,
                                     justify="left", anchor="w")
        self.lbl_canh_bao.pack(fill="x", padx=10, pady=(10, 4))
        cot = [("ma", "Ô", 60, "center"), ("ten", "Sản phẩm", 220, "w"), ("gia", "Giá bán", 110, "e"),
               ("von", "Giá vốn", 110, "e"), ("sl", "Tồn", 70, "center"), ("sc", "Sức chứa", 90, "center"),
               ("tt", "Trạng thái", 140, "center")]
        khung, self.tree_kho = tao_tree(self.tab_kho, cot)
        khung.pack(fill="both", expand=True, padx=10, pady=4)
        self.tree_kho.tag_configure("het", foreground="#ff6b81")
        self.tree_kho.tag_configure("sap", foreground=CAM)
        thanh = tk.Frame(self.tab_kho, bg=NEN_TOI)
        thanh.pack(fill="x", padx=10, pady=8)
        for text, cmd in [("Nhập thêm hàng", self.nhap_them), ("Đổ đầy tất cả", self.do_day),
                          ("Thêm / sửa ô", self.them_sua), ("Xóa ô", self.xoa_o)]:
            tao_nut(thanh, text, cmd, size=10).pack(side="left", padx=4)

    def xay_tab_ket(self):
        self.lbl_ket_tong = tk.Label(self.tab_ket, text="", bg=NEN_TOI, fg=VANG, font=("Segoe UI", 18, "bold"),
                                     anchor="w")
        self.lbl_ket_tong.pack(fill="x", padx=14, pady=(14, 2))
        self.lbl_ket_phu = tk.Label(self.tab_ket, text="", bg=NEN_TOI, fg=CHU_PHU, font=("Segoe UI", 10),
                                    justify="left", anchor="w", wraplength=1000)
        self.lbl_ket_phu.pack(fill="x", padx=14)
        cot = [("menh", "Mệnh giá", 160, "e"), ("sl", "Số tờ", 110, "center"), ("tien", "Thành tiền", 190, "e"),
               ("dung", "Dùng để thối", 180, "center")]
        khung, self.tree_ket = tao_tree(self.tab_ket, cot)
        khung.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree_ket.tag_configure("het", foreground="#ff6b81")

    def xay_tab_gd(self):
        loc = tk.Frame(self.tab_gd, bg=NEN_TOI)
        loc.pack(fill="x", padx=10, pady=10)
        tk.Label(loc, text="Ngày (YYYY-MM-DD):", bg=NEN_TOI, fg=CHU).pack(side="left")
        self.e_ngay = tk.Entry(loc, width=14, bg="#241a52", fg="white", insertbackground="white", relief="flat")
        self.e_ngay.pack(side="left", padx=(4, 14), ipady=4)
        tk.Label(loc, text="Ô:", bg=NEN_TOI, fg=CHU).pack(side="left")
        self.e_slot = tk.Entry(loc, width=8, bg="#241a52", fg="white", insertbackground="white", relief="flat")
        self.e_slot.pack(side="left", padx=(4, 14), ipady=4)
        tao_nut(loc, "Lọc", self.lam_moi_gd, size=10).pack(side="left", padx=4)
        tao_nut(loc, "Bỏ lọc", self.bo_loc, size=10, bg="#3a2a7a").pack(side="left", padx=4)
        cot = [("ma", "Mã GD", 75, "center"), ("tg", "Thời gian", 150, "center"), ("nguon", "Nguồn", 75, "center"),
               ("slot", "Ô", 45, "center"), ("ten", "Sản phẩm", 170, "w"), ("sl", "SL", 40, "center"),
               ("gia", "Đơn giá", 90, "e"), ("nhan", "Tiền nhận", 100, "e"), ("thoi", "Tiền thối", 100, "e")]
        khung, self.tree_gd = tao_tree(self.tab_gd, cot)
        khung.pack(fill="both", expand=True, padx=10, pady=4)
        self.tree_gd.tag_configure("that", foreground=VANG)
        self.tree_gd.tag_configure("gia_lap", foreground=CHU)
        self.tree_gd.tag_configure("cu", foreground="#8a7fb5")
        self.lbl_tong_gd = tk.Label(self.tab_gd, text="", bg=NEN_TOI, fg=VANG, font=("Segoe UI", 11, "bold"))
        self.lbl_tong_gd.pack(anchor="w", padx=10, pady=8)

    def xay_tab_nhap(self):
        cot = [("tg", "Thời gian", 160, "center"), ("slot", "Ô", 50, "center"), ("ten", "Sản phẩm", 210, "w"),
               ("sl", "Số lượng nhập", 110, "center"), ("ton", "Tồn sau nhập", 110, "center"),
               ("chi", "Chi phí (trừ két)", 140, "e"), ("nguon", "Nguồn", 100, "center")]
        khung, self.tree_nhap = tao_tree(self.tab_nhap, cot)
        khung.pack(fill="both", expand=True, padx=10, pady=10)

    def xay_tab_lai(self):
        thanh = tk.Frame(self.tab_lai, bg=NEN_TOI)
        thanh.pack(fill="x", padx=10, pady=10)
        tao_nut(thanh, "Làm mới", self.lam_moi, size=10).pack(side="left")
        self.txt_lai = tk.Text(self.tab_lai, bg=CARD_BG, fg=CHU, font=("Consolas", 10), relief="flat",
                               padx=14, pady=10, state="disabled", insertbackground="white")
        self.txt_lai.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def xay_tab_quy(self):
        self.lbl_quy = tk.Label(self.tab_quy, text="", bg=NEN_TOI, fg=CHU_PHU, font=("Segoe UI", 10), anchor="w")
        self.lbl_quy.pack(fill="x", padx=12, pady=(10, 0))
        cot = [("tg", "Ngày giờ", 160, "center"), ("loai", "Loại", 170, "w"), ("nd", "Nội dung", 330, "w"),
               ("tien", "Thu / chi", 120, "e"), ("ket", "Két sau đó", 130, "e")]
        khung, self.tree_quy = tao_tree(self.tab_quy, cot)
        khung.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree_quy.tag_configure("thu", foreground=XANH_LA)
        self.tree_quy.tag_configure("chi", foreground=DO_NHAT)

    def xay_tab_bao_cao(self):
        thanh = tk.Frame(self.tab_bc, bg=NEN_TOI)
        thanh.pack(fill="x", padx=10, pady=10)
        tao_nut(thanh, "Làm mới báo cáo", self.lam_moi, size=10).pack(side="left")
        self.txt = tk.Text(self.tab_bc, bg=CARD_BG, fg=CHU, font=("Consolas", 11), relief="flat",
                           padx=14, pady=10, state="disabled", insertbackground="white")
        self.txt.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def lam_moi(self):
        self.lam_moi_kho()
        self.lam_moi_ket()
        self.lam_moi_gd()
        self.lam_moi_nhap()
        self.lam_moi_lai()
        self.lam_moi_quy()
        self.lam_moi_bao_cao()
        self.lam_moi_tin_nhap()
        self.app.ve_cards()

    def lam_moi_tin_nhap(self):
        noi_dung, mau = self.app.tin_nhap_cuoi
        self.lbl_tin_nhap.config(text=noi_dung or "▣ Chưa có lần nhập hàng nào kể từ khi mở máy.", fg=mau)

    def lam_moi_kho(self):
        dang_chon = self.tree_kho.selection()
        for i in self.tree_kho.get_children():
            self.tree_kho.delete(i)
        canh_bao = []
        for ma, s in sorted(self.dl["slots"].items()):
            tt = trang_thai_slot(s)
            tag = ()
            if s["so_luong"] == 0:
                tag = ("het",)
                canh_bao.append(f"[HẾT] Ô {ma} - {s['ten']}")
            elif s["so_luong"] <= NGUONG_SAP_HET:
                tag = ("sap",)
                canh_bao.append(f"[SẮP HẾT] Ô {ma} - {s['ten']} (còn {s['so_luong']})")
            self.tree_kho.insert("", "end", iid=ma, tags=tag,
                                 values=(ma, s["ten"], tien(s["gia"]), tien(s["gia_von"]), s["so_luong"],
                                         s["suc_chua"], tt))
        if dang_chon and self.tree_kho.exists(dang_chon[0]):
            self.tree_kho.selection_set(dang_chon[0])
        if canh_bao:
            self.lbl_canh_bao.config(text="⚠ CẢNH BÁO TỒN KHO:  " + "   |   ".join(canh_bao), fg=CAM)
        else:
            self.lbl_canh_bao.config(text="✔ Tất cả các ô đều đủ hàng.", fg=XANH_LA)

    def lam_moi_ket(self):
        ket = self.dl["ket"]
        for i in self.tree_ket.get_children():
            self.tree_ket.delete(i)
        for m in MENH_KET:
            n = ket.get(m, 0)
            thoi_duoc = m in MENH_GIA_THOI
            tag = ("het",) if thoi_duoc and n == 0 else ()
            self.tree_ket.insert("", "end", tags=tag,
                                 values=(tien(m), n, tien(m * n), "Có" if thoi_duoc else "Không (chỉ giữ)"))
        self.lbl_ket_tong.config(text=f"Tổng tiền trong két: {tien(tong_ket(ket))}")
        self.lbl_ket_phu.config(
            text=f"Két ban đầu: {tien(tong_ket(self.dl['ket_ban_dau']))} (khởi tạo lúc {self.dl['khoi_dau']}). "
                 f"Máy chỉ thối bằng các tờ từ {tien(max(MENH_GIA_THOI))} trở xuống. Khách bỏ số tiền mà máy không thối đủ "
                 f"thì tờ tiền đó được trả lại. Tiền nhập hàng được trả từ két.")

    def lam_moi_gd(self):
        for i in self.tree_gd.get_children():
            self.tree_gd.delete(i)
        ngay = self.e_ngay.get().strip()
        slot = self.e_slot.get().strip().upper()
        ds = ([(g, "Thật") for g in self.dl["gd_that"]] + [(g, "Giả lập") for g in self.dl["gd_gia_lap"]]
              + [(g, "Cũ") for g in self.dl["gd_cu"]])
        if ngay:
            ds = [x for x in ds if x[0]["thoi_gian"].startswith(ngay)]
        if slot:
            ds = [x for x in ds if x[0]["slot"] == slot]
        ds.sort(key=lambda x: x[0]["thoi_gian"], reverse=True)
        dem = {"Thật": [0, 0], "Giả lập": [0, 0], "Cũ": [0, 0]}
        tag_theo_nguon = {"Thật": "that", "Giả lập": "gia_lap", "Cũ": "cu"}
        for g, nguon in ds:
            dem[nguon][0] += 1
            dem[nguon][1] += g["doanh_thu"]
            self.tree_gd.insert("", "end", tags=(tag_theo_nguon[nguon],),
                                values=(g["ma_gd"], g["thoi_gian"], nguon, g["slot"], g["ten"], g.get("so_luong", 1),
                                        tien(g["don_gia"]), tien(g["tien_nhan"]), tien(g["tien_thoi"])))
        text = (f"Thật: {dem['Thật'][0]} GD - {tien(dem['Thật'][1])}   |   "
                f"Giả lập: {dem['Giả lập'][0]} GD - {tien(dem['Giả lập'][1])}")
        if dem["Cũ"][0]:
            text += f"   |   Cũ (trước khi có két, không tính lãi/lỗ): {dem['Cũ'][0]} GD"
        self.lbl_tong_gd.config(text=text)

    def bo_loc(self):
        self.e_ngay.delete(0, "end")
        self.e_slot.delete(0, "end")
        self.lam_moi_gd()

    def lam_moi_nhap(self):
        for i in self.tree_nhap.get_children():
            self.tree_nhap.delete(i)
        for n in reversed(self.dl["nhap_hang"]):
            chi = tien(n["chi_phi"]) if "chi_phi" in n else "-"
            self.tree_nhap.insert("", "end", values=(n["thoi_gian"], n["slot"], n["ten"], n["so_luong"],
                                                     n["ton_sau"], chi, n.get("nguon", "Quản trị")))

    def lam_moi_lai(self):
        self.txt_lai.config(state="normal")
        self.txt_lai.delete("1.0", "end")
        self.txt_lai.insert("1.0", van_ban_lai_lo(self.dl))
        self.txt_lai.config(state="disabled")

    def lam_moi_quy(self):
        for i in self.tree_quy.get_children():
            self.tree_quy.delete(i)
        tat_ca = so_quy(self.dl)
        gan_day = tat_ca[-300:]
        for tg, loai, noi_dung, so_tien, so_du in reversed(gan_day):
            self.tree_quy.insert("", "end", tags=("thu" if so_tien >= 0 else "chi",),
                                 values=(tg, loai, noi_dung, tien_dau(so_tien), tien(so_du)))
        self.lbl_quy.config(
            text=f"Ghi nhận từ {self.dl['khoi_dau']} - hiển thị {len(gan_day)}/{len(tat_ca)} mục gần nhất, "
                 f"két ban đầu {tien(tong_ket(self.dl['ket_ban_dau']))}")

    def lam_moi_bao_cao(self):
        gds = tat_ca_gd(self.dl)
        slots = self.dl["slots"]
        dong = ["=== TỔNG QUAN (khách thật + giả lập) ==="]
        dong.append(f"Số giao dịch        : {len(gds)}  (thật {len(self.dl['gd_that'])}, giả lập {len(self.dl['gd_gia_lap'])})")
        dong.append(f"Tổng sản phẩm đã bán: {sum(g['so_luong'] for g in gds)}")
        dong.append(f"Tổng doanh thu      : {tien(sum(g['doanh_thu'] for g in gds))}")
        dong.append(f"Sản phẩm còn lại    : {sum(s['so_luong'] for s in slots.values())}")
        dong.append(f"Giá trị tồn kho     : {tien(sum(s['so_luong'] * s['gia'] for s in slots.values()))}")
        theo_ngay = {}
        theo_slot = {}
        for g in gds:
            ngay = g["thoi_gian"][:10]
            theo_ngay[ngay] = theo_ngay.get(ngay, 0) + g["doanh_thu"]
            if g["slot"] not in theo_slot:
                theo_slot[g["slot"]] = [g["ten"], 0, 0]
            theo_slot[g["slot"]][1] += g["so_luong"]
            theo_slot[g["slot"]][2] += g["doanh_thu"]
        dong.append("")
        dong.append("=== DOANH THU THEO NGÀY ===")
        if theo_ngay:
            for ngay in sorted(theo_ngay):
                dong.append(f"{ngay}  :  {tien(theo_ngay[ngay])}")
        else:
            dong.append("Chưa có giao dịch.")
        dong.append("")
        dong.append("=== DOANH THU THEO Ô (cao -> thấp) ===")
        if theo_slot:
            for ma, (ten, sl, dt) in sorted(theo_slot.items(), key=lambda x: x[1][2], reverse=True):
                dong.append(f"Ô {ma:<4}{ten:<20} bán {sl:>3} cái  |  {tien(dt)}")
        else:
            dong.append("Chưa có giao dịch.")
        dong.append("")
        dong.append("=== CẦN NHẬP HÀNG ===")
        can = [(m, s) for m, s in sorted(slots.items()) if s["so_luong"] <= NGUONG_SAP_HET]
        if can:
            for m, s in can:
                dong.append(f"Ô {m:<4}{s['ten']:<20} còn {s['so_luong']}, nhập thêm tối đa {s['suc_chua'] - s['so_luong']}")
        else:
            dong.append("Không có ô nào cần nhập hàng.")
        self.txt.config(state="normal")
        self.txt.delete("1.0", "end")
        self.txt.insert("1.0", "\n".join(dong))
        self.txt.config(state="disabled")

    def ma_dang_chon(self):
        sel = self.tree_kho.selection()
        if not sel:
            messagebox.showinfo("Chọn ô", "Hãy chọn một dòng trong bảng tồn kho trước.", parent=self.win)
            return None
        return sel[0]

    def bao_thieu_tien(self, kq, so, gia_von):
        if kq["ket"] < kq["can"]:
            ly_do = f"két chỉ có {tien(kq['ket'])}"
        else:
            ly_do = "két không có đủ tờ tiền để trả đúng số tiền này"
        messagebox.showerror("Không đủ tiền nhập hàng",
                             f"Cần {tien(kq['can'])} để nhập {so} sản phẩm ({tien(gia_von)}/cái) nhưng {ly_do}.",
                             parent=self.win)

    def nhap_them(self):
        ma = self.ma_dang_chon()
        if ma is None:
            return
        s = self.dl["slots"][ma]
        con_trong = s["suc_chua"] - s["so_luong"]
        if con_trong <= 0:
            messagebox.showinfo("Ô đã đầy", f"Ô {ma} đã đầy.", parent=self.win)
            return
        so = simpledialog.askinteger(
            "Nhập hàng",
            f"Ô {ma} - {s['ten']}\nĐang có {s['so_luong']}, nhập thêm tối đa {con_trong}.\n"
            f"Giá vốn {tien(s['gia_von'])}/cái, tiền sẽ trừ vào két:",
            parent=self.win, minvalue=1, maxvalue=con_trong)
        if not so:
            return
        kq = nhap_hang_tra_tien(self.dl, ma, so, "Quản trị", False)
        if not kq["ok"]:
            self.bao_thieu_tien(kq, so, s["gia_von"])
            return
        self.app.tin_nhap_cuoi = (
            f"▣ {bay_gio()[11:]}  Quản trị nhập: Ô {ma} +{kq['so']} (-{tien(kq['chi_phi'])}) | "
            f"Két còn {tien(tong_ket(self.dl['ket']))}", HONG)
        luu_du_lieu(self.dl)
        self.lam_moi()

    def do_day(self):
        tong_sp = 0
        tong_chi = 0
        chua_day = []
        for ma, s in sorted(self.dl["slots"].items()):
            them = s["suc_chua"] - s["so_luong"]
            if them <= 0:
                continue
            kq = nhap_hang_tra_tien(self.dl, ma, them, "Quản trị", True)
            if kq["ok"]:
                tong_sp += kq["so"]
                tong_chi += kq["chi_phi"]
                if kq["so"] < them:
                    chua_day.append(ma)
            else:
                chua_day.append(ma)
        self.app.tin_nhap_cuoi = (
            f"▣ {bay_gio()[11:]}  Quản trị đổ đầy: +{tong_sp} sản phẩm (-{tien(tong_chi)}) | "
            f"Két còn {tien(tong_ket(self.dl['ket']))}", HONG)
        luu_du_lieu(self.dl)
        self.lam_moi()
        noi_dung = f"Đã bổ sung {tong_sp} sản phẩm, chi {tien(tong_chi)} từ két."
        if chua_day:
            noi_dung += "\nCác ô chưa đầy vì két không đủ tiền: " + ", ".join(chua_day)
        else:
            noi_dung += "\nTất cả các ô đã đầy."
        messagebox.showinfo("Hoàn tất", noi_dung, parent=self.win)

    def them_sua(self):
        sel = self.tree_kho.selection()
        ma = simpledialog.askstring("Thêm / sửa ô", "Mã ô (ô mới sẽ được tạo):", parent=self.win,
                                    initialvalue=sel[0] if sel else "")
        if not ma or not ma.strip():
            return
        ma = ma.strip().upper()
        cu = self.dl["slots"].get(ma, {"ten": "", "gia": 10000, "gia_von": 7000, "so_luong": 0, "suc_chua": 10})
        moi = ma not in self.dl["slots"]
        ten = simpledialog.askstring("Thêm / sửa ô", "Tên sản phẩm:", parent=self.win, initialvalue=cu["ten"])
        if not ten or not ten.strip():
            return
        gia = simpledialog.askinteger("Thêm / sửa ô", "Giá bán (đ, bội số của 1.000):", parent=self.win,
                                      initialvalue=cu["gia"], minvalue=DON_VI_TIEN)
        if not gia:
            return
        if gia % DON_VI_TIEN:
            messagebox.showerror("Lỗi", "Giá bán phải là bội số của 1.000đ (máy thối tiền theo tờ 1.000đ).",
                                 parent=self.win)
            return
        gia_von = simpledialog.askinteger("Thêm / sửa ô", "Giá vốn mỗi cái (đ, bội số của 1.000):", parent=self.win,
                                          initialvalue=cu["gia_von"] if not moi else gia_von_mac_dinh(gia),
                                          minvalue=DON_VI_TIEN)
        if not gia_von:
            return
        if gia_von % DON_VI_TIEN:
            messagebox.showerror("Lỗi", "Giá vốn phải là bội số của 1.000đ (máy trả tiền nhập hàng theo tờ 1.000đ).",
                                 parent=self.win)
            return
        suc = simpledialog.askinteger("Thêm / sửa ô", "Sức chứa:", parent=self.win,
                                      initialvalue=cu["suc_chua"], minvalue=1)
        if not suc:
            return
        ten = ten.strip()
        so_luong = cu["so_luong"]
        if not moi and ten != cu["ten"]:
            so_luong = 0
        if so_luong > suc:
            messagebox.showerror("Lỗi", "Sức chứa mới nhỏ hơn số lượng hiện có.", parent=self.win)
            return
        self.dl["slots"][ma] = {"ten": ten, "gia": gia, "gia_von": gia_von, "so_luong": so_luong, "suc_chua": suc}
        luu_du_lieu(self.dl)
        self.lam_moi()

    def xoa_o(self):
        ma = self.ma_dang_chon()
        if ma is None:
            return
        if messagebox.askyesno("Xóa ô", f"Xóa ô {ma} - {self.dl['slots'][ma]['ten']}?", parent=self.win):
            del self.dl["slots"][ma]
            luu_du_lieu(self.dl)
            self.lam_moi()


class MayBanHang:
    def __init__(self, root):
        self.root = root
        self.dl = tai_du_lieu()
        self.t = 0.0
        self.w = 1000
        self.h = 720
        self.strips = []
        self.stars = []
        self.the_list = []
        self.cua_so_the = []
        self.cau_hien = -1
        self.quan_tri = None
        self.tin_nhap_cuoi = ("", HONG)
        self.nhap_han = time.time() + CHU_KY_NHAP_HANG
        self.loi_da_bao = ""
        luu_du_lieu(self.dl)
        root.title("✦ Máy Bán Hàng Huyền Bí ✦")
        root.geometry("1000x720")
        root.minsize(760, 560)
        self.canvas = tk.Canvas(root, highlightthickness=0, bg=NEN_TOI)
        self.canvas.pack(fill="both", expand=True)
        self.tieu_de = self.canvas.create_text(500, 48, text="✦  MÁY BÁN HÀNG HUYỀN BÍ  ✦",
                                               font=("Segoe UI", 28, "bold"), fill=CHU)
        self.phu_de = self.canvas.create_text(500, 92, text="", font=("Segoe UI", 13, "italic"), fill=CHU_PHU)
        self.thong_bao = self.canvas.create_text(500, 120, text="", font=("Segoe UI", 11, "bold"), fill=XANH_LA)
        self.nut_admin = tao_nut(root, "⚙ Quản trị", self.mo_quan_tri, bg="#3a2a7a", size=10)
        self.cua_so_admin = self.canvas.create_window(980, 14, anchor="ne", window=self.nut_admin)
        for _ in range(SO_SAO):
            sid = self.canvas.create_oval(0, 0, 0, 0, width=0, fill="#ffffff")
            self.stars.append((sid, random.random(), random.random(), random.random() * 6.28, random.choice([1, 1, 2, 2, 3])))
        self.ve_cards()
        self.canvas.bind("<Configure>", self.khi_doi_kich_thuoc)
        self.tick()

    def khi_doi_kich_thuoc(self, e):
        if e.width < 50 or e.height < 50:
            return
        self.w, self.h = e.width, e.height
        self.canvas.delete("nen")
        self.strips = []
        for i in range(SO_DAI):
            y0 = self.h * i / SO_DAI
            y1 = self.h * (i + 1) / SO_DAI + 1
            self.strips.append(self.canvas.create_rectangle(0, y0, self.w, y1, width=0, tags="nen"))
        self.canvas.tag_lower("nen")
        for sid, fx, fy, ph, r in self.stars:
            x, y = fx * self.w, fy * self.h
            self.canvas.coords(sid, x - r, y - r, x + r, y + r)
        self.canvas.coords(self.tieu_de, self.w / 2, 48)
        self.canvas.coords(self.phu_de, self.w / 2, 92)
        self.canvas.coords(self.thong_bao, self.w / 2, 120)
        self.canvas.coords(self.cua_so_admin, self.w - 16, 14)
        self.bo_tri()
        self.cap_nhat_mau()

    def cap_nhat_mau(self):
        t = self.t
        n = len(self.strips)
        for i, sid in enumerate(self.strips):
            f = i / max(1, n - 1)
            h = 0.70 + 0.09 * math.sin(t * 0.6 + f * 2.2)
            l = 0.07 + 0.09 * f + 0.02 * math.sin(t * 0.9 + f * 3)
            self.canvas.itemconfig(sid, fill=hls_hex(h, l, 0.75))
        for sid, fx, fy, ph, r in self.stars:
            b = 0.5 + 0.5 * math.sin(t * 2 + ph)
            self.canvas.itemconfig(sid, fill="#%02x%02x%02x" % (int(90 + 150 * b), int(80 + 140 * b), int(150 + 105 * b)))
        self.canvas.itemconfig(self.tieu_de, fill=hls_hex(0.72 + 0.12 * math.sin(t * 0.8), 0.78, 0.9))
        for i, the in enumerate(self.the_list):
            the.config(highlightbackground=hls_hex(0.72 + 0.12 * math.sin(t * 0.8 + i * 0.6), 0.58, 0.85))
        idx = int(t / 6) % len(CAU_DAN)
        if idx != self.cau_hien:
            self.cau_hien = idx
            self.canvas.itemconfig(self.phu_de, text=CAU_DAN[idx])

    def nhap_con_lai(self):
        return max(0, self.nhap_han - time.time())

    def kiem_tra_nhap_hang(self):
        if time.time() < self.nhap_han:
            return
        self.nhap_han = time.time() + CHU_KY_NHAP_HANG
        slots = self.dl["slots"]
        chua_day = [m for m, s in slots.items() if s["so_luong"] < s["suc_chua"]]
        if not chua_day:
            return
        sap_het = sorted([m for m in chua_day if slots[m]["so_luong"] <= NGUONG_SAP_HET],
                         key=lambda m: slots[m]["so_luong"])
        so_o = random.randint(1, min(3, len(chua_day)))
        chon = sap_het[:so_o]
        con_lai = [m for m in chua_day if m not in chon]
        random.shuffle(con_lai)
        chon += con_lai[:so_o - len(chon)]
        tong_chi = 0
        cho_khach = []
        cho_admin = []
        thieu = []
        for m in chon:
            s = slots[m]
            con_trong = s["suc_chua"] - s["so_luong"]
            them = random.randint(max(1, con_trong // 2), con_trong)
            kq = nhap_hang_tra_tien(self.dl, m, them, "Tự động", True)
            if kq["ok"]:
                tong_chi += kq["chi_phi"]
                cho_khach.append(f"Ô {m} +{kq['so']}")
                cho_admin.append(f"Ô {m} +{kq['so']} (-{tien(kq['chi_phi'])})")
            else:
                thieu.append(f"Ô {m}")
        luu_du_lieu(self.dl)
        self.ve_cards()
        gio = bay_gio()[11:]
        if cho_khach:
            self.canvas.itemconfig(self.thong_bao, text=f"▣ {gio}  Hàng mới về: " + ", ".join(cho_khach), fill=XANH_LA)
        phan = []
        if cho_admin:
            phan.append("Nhập tự động: " + ", ".join(cho_admin) + f" | Tổng -{tien(tong_chi)}")
        if thieu:
            phan.append("KHÔNG ĐỦ TIỀN trong két để nhập: " + ", ".join(thieu))
        phan.append(f"Két còn {tien(tong_ket(self.dl['ket']))}")
        self.tin_nhap_cuoi = (f"▣ {gio}  " + " | ".join(phan), CAM if thieu else HONG)
        if self.quan_tri is not None and self.quan_tri.win.winfo_exists():
            self.quan_tri.lam_moi()

    def tick(self):
        self.t += 0.04
        self.kiem_tra_nhap_hang()
        loi = TRANG_THAI["loi"]
        if loi != self.loi_da_bao:
            self.loi_da_bao = loi
            if loi:
                self.canvas.itemconfig(self.thong_bao, text=f"⚠ Không ghi được dữ liệu vào {THU_MUC_DL}: {loi}", fill=CAM)
            else:
                self.canvas.itemconfig(self.thong_bao, text="", fill=XANH_LA)
        self.cap_nhat_mau()
        self.root.after(70, self.tick)

    def ban_chay_nhat(self):
        dem = {}
        for g in tat_ca_gd(self.dl):
            dem[g["slot"]] = dem.get(g["slot"], 0) + g["so_luong"]
        if not dem:
            return None
        ma = max(dem, key=dem.get)
        return ma if ma in self.dl["slots"] else None

    def ve_cards(self):
        for wid in self.cua_so_the:
            self.canvas.delete(wid)
        for the in self.the_list:
            the.destroy()
        self.the_list = []
        self.cua_so_the = []
        best = self.ban_chay_nhat()
        for ma, s in sorted(self.dl["slots"].items()):
            the = self.tao_the(ma, s, ma == best)
            wid = self.canvas.create_window(0, 0, anchor="nw", window=the, width=CW, height=CH)
            self.the_list.append(the)
            self.cua_so_the.append(wid)
        so_can = sum(1 for s in self.dl["slots"].values() if s["so_luong"] <= NGUONG_SAP_HET)
        self.nut_admin.config(text=f"⚠ Quản trị ({so_can})" if so_can else "⚙ Quản trị",
                              bg="#b3472f" if so_can else "#3a2a7a")
        self.bo_tri()

    def bo_tri(self):
        cols = max(1, (self.w - 40 + GAP) // (CW + GAP))
        tong_w = cols * CW + (cols - 1) * GAP
        x0 = (self.w - tong_w) / 2
        y0 = 150
        for idx, wid in enumerate(self.cua_so_the):
            r, c = divmod(idx, cols)
            self.canvas.coords(wid, x0 + c * (CW + GAP), y0 + r * (CH + GAP))

    def tao_the(self, ma, s, ban_chay):
        the = tk.Frame(self.canvas, width=CW, height=CH, bg=CARD_BG, highlightthickness=2,
                       highlightbackground=TIM, highlightcolor=TIM)
        the.pack_propagate(False)
        het = s["so_luong"] <= 0
        nut = tao_nut(the, "ĐÃ HẾT HÀNG" if het else "✦ MUA NGAY ✦",
                      (lambda m=ma: self.thanh_toan(m)), state="disabled" if het else "normal")
        nut.pack(side="bottom", fill="x", padx=14, pady=(0, 12))
        hang = tk.Frame(the, bg=CARD_BG)
        hang.pack(fill="x", padx=14, pady=(10, 0))
        tk.Label(hang, text=f"✦ Ô {ma}", bg=CARD_BG, fg=CHU_PHU, font=("Segoe UI", 10, "bold")).pack(side="left")
        if ban_chay:
            tk.Label(hang, text="★ BÁN CHẠY", bg=CARD_BG, fg=HONG, font=("Segoe UI", 10, "bold")).pack(side="right")
        tk.Label(the, text=s["ten"], bg=CARD_BG, fg=CHU, font=("Segoe UI", 16, "bold"),
                 wraplength=CW - 30, justify="left", anchor="w").pack(fill="x", padx=14, pady=(6, 0))
        tk.Label(the, text=tien(s["gia"]), bg=CARD_BG, fg=VANG, font=("Segoe UI", 20, "bold"),
                 anchor="w").pack(fill="x", padx=14)
        if het:
            text, mau = "✖ Đã cạn kiệt - hẹn bạn lần sau", "#8a7fb5"
        elif s["so_luong"] <= NGUONG_SAP_HET:
            text, mau = f"⚡ Chỉ còn {s['so_luong']} - nhanh tay kẻo lỡ!", CAM
        else:
            text, mau = f"Còn {s['so_luong']} sản phẩm", XANH_LA
        tk.Label(the, text=text, bg=CARD_BG, fg=mau, font=("Segoe UI", 10, "bold"),
                 anchor="w").pack(fill="x", padx=14, pady=(2, 0))
        return the

    def can_giua(self, win):
        win.update_idletasks()
        x = self.root.winfo_rootx() + (self.root.winfo_width() - win.winfo_width()) // 2
        y = self.root.winfo_rooty() + (self.root.winfo_height() - win.winfo_height()) // 2
        win.geometry(f"+{max(0, x)}+{max(0, y)}")

    def hop_thong_bao(self, tieu_de, noi_dung, mau=VANG):
        hop = tk.Toplevel(self.root)
        hop.title("Thông báo")
        hop.configure(bg=CARD_BG)
        hop.transient(self.root)
        hop.resizable(False, False)
        tk.Label(hop, text=tieu_de, bg=CARD_BG, fg=mau, font=("Segoe UI", 18, "bold")).pack(padx=30, pady=(22, 8))
        tk.Label(hop, text=noi_dung, bg=CARD_BG, fg=CHU, font=("Segoe UI", 11), wraplength=380,
                 justify="center").pack(padx=30, pady=6)
        tao_nut(hop, "Đóng", hop.destroy).pack(pady=(10, 22))
        self.can_giua(hop)
        hop.grab_set()

    def thanh_toan(self, ma):
        s = self.dl["slots"].get(ma)
        if s is None or s["so_luong"] <= 0:
            return
        gia = s["gia"]
        dlg = tk.Toplevel(self.root)
        dlg.title("Thanh toán")
        dlg.configure(bg=CARD_BG)
        dlg.transient(self.root)
        dlg.resizable(False, False)
        to_nap = {}
        xong = [False]
        tk.Label(dlg, text=f"✦ {s['ten']} ✦", bg=CARD_BG, fg=CHU, font=("Segoe UI", 18, "bold")).pack(padx=30, pady=(20, 2))
        tk.Label(dlg, text=f"Ô {ma}  -  {tien(gia)}", bg=CARD_BG, fg=VANG, font=("Segoe UI", 14, "bold")).pack()
        lbl_nap = tk.Label(dlg, text="", bg=CARD_BG, fg=XANH_LA, font=("Segoe UI", 12, "bold"))
        lbl_nap.pack(pady=(12, 0))
        lbl_thieu = tk.Label(dlg, text="", bg=CARD_BG, fg=CAM, font=("Segoe UI", 12, "bold"))
        lbl_thieu.pack(pady=(0, 6))
        lbl_loi = tk.Label(dlg, text="", bg=CARD_BG, fg=DO_NHAT, font=("Segoe UI", 11, "bold"),
                           wraplength=360, justify="center")
        lbl_loi.pack(pady=(0, 6))
        luoi = tk.Frame(dlg, bg=CARD_BG)
        luoi.pack(padx=20)

        def tong_nap():
            return sum(m * n for m, n in to_nap.items())

        def cap_nhat():
            lbl_nap.config(text=f"Đã nạp: {tien(tong_nap())}")
            lbl_thieu.config(text=f"Còn thiếu: {tien(max(0, gia - tong_nap()))}")

        def nap(menh):
            if xong[0]:
                return
            if not co_the_nhan_to(self.dl, gia, tong_nap(), menh):
                lbl_loi.config(text=f"Máy không đủ tiền để thối cho tờ {tien(menh)}.\n"
                                    f"Đã trả lại tờ {tien(menh)} - vui lòng dùng tờ nhỏ hơn.")
                return
            lbl_loi.config(text="")
            to_nap[menh] = to_nap.get(menh, 0) + 1
            cap_nhat()
            if tong_nap() >= gia:
                xong[0] = True
                dlg.destroy()
                self.hoan_tat_ban(ma, dict(to_nap))

        def huy():
            if xong[0]:
                return
            xong[0] = True
            tong = tong_nap()
            dlg.destroy()
            if tong > 0:
                self.hop_thong_bao("Đã hủy giao dịch", f"Hoàn lại {tien(tong)}\n{chuoi_to(to_nap)}", DO_NHAT)

        for i, menh in enumerate(MENH_GIA_NHAN):
            tao_nut(luoi, tien(menh), (lambda m=menh: nap(m)), size=10).grid(
                row=i // 3, column=i % 3, padx=4, pady=4, sticky="ew")
        tao_nut(dlg, "Hủy & hoàn tiền", huy, bg="#b3472f", size=10).pack(pady=(12, 20))
        dlg.protocol("WM_DELETE_WINDOW", huy)
        cap_nhat()
        self.can_giua(dlg)
        dlg.grab_set()

    def hoan_tat_ban(self, ma, to_nap):
        kq = ban_hang(self.dl, ma, 1, to_nap, "that")
        if not kq["ok"]:
            tong = sum(m * n for m, n in to_nap.items())
            if kq["ly_do"] == "khong_thoi_duoc":
                ly_do = "Máy không đủ tiền để thối."
            elif kq["ly_do"] == "het_hang":
                ly_do = "Sản phẩm vừa hết hàng."
            else:
                ly_do = "Giá sản phẩm vừa thay đổi."
            self.hop_thong_bao("Giao dịch bị hủy", f"{ly_do}\nĐã trả lại {tien(tong)}\n{chuoi_to(to_nap)}", DO_NHAT)
            self.ve_cards()
            return
        gd = kq["gd"]
        luu_du_lieu(self.dl)
        self.ve_cards()
        if self.quan_tri is not None and self.quan_tri.win.winfo_exists():
            self.quan_tri.lam_moi()
        noi_dung = f"Bạn đã sở hữu: {gd['ten']}\nMã giao dịch: {gd['ma_gd']}"
        if gd["tien_thoi"] > 0:
            noi_dung += f"\n\nTiền thối: {tien(gd['tien_thoi'])}\n{chuoi_to(kq['to_thoi'])}"
        noi_dung += "\n\n✦ " + random.choice(LOI_TIEN_TRI)
        self.hop_thong_bao("Thanh toán thành công!", noi_dung, XANH_LA)

    def mo_quan_tri(self):
        if self.quan_tri is not None and self.quan_tri.win.winfo_exists():
            self.quan_tri.win.lift()
            return
        mk = simpledialog.askstring("Quản trị viên", "Nhập mật khẩu:", show="*", parent=self.root)
        if mk is None:
            return
        if mk != MAT_KHAU_ADMIN:
            messagebox.showerror("Sai mật khẩu", "Mật khẩu không đúng.", parent=self.root)
            return
        self.quan_tri = QuanTri(self)


def main():
    root = tk.Tk()
    MayBanHang(root)
    root.mainloop()


if __name__ == "__main__":
    main()
