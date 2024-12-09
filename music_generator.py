import numpy as np
import wave
import struct
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

# Hàm tính toán tần số của nốt nhạc
def get_frequency(note):
    # Thang âm chromatic (chỉ bao gồm tên nốt mà không có số)
    chromatic_scale = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    base_note = note[:-1]  # Tên nốt (ví dụ: G từ G4)
    octave = int(note[-1])  # Quãng tám (ví dụ: 4 từ G4)

    # Xác định vị trí của nốt trong toàn bộ thang âm
    semitone_offset = chromatic_scale.index(base_note)  # Vị trí trong một quãng tám
    note_position = (octave * 12) + semitone_offset - 9  # Điều chỉnh để A4 = 49

    # Tính tần số theo công thức
    frequency = 440 * 2 ** ((note_position - 49) / 12)  # A4 là nốt 49, tần số 440Hz
    return frequency

# Hàm tạo sóng âm cho một nốt nhạc với các yếu tố ADSR và harmonics
def generate_sound(note, duration_sec, sample_rate, instrument="piano"):
    frequency = get_frequency(note)  # Tính tần số động
    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), endpoint=False)

    # Điều chỉnh tần số nhỏ theo nhạc cụ
    if instrument == "guitar":
        frequency *= 0.99  # Giảm nhẹ tần số
    else:
        frequency = frequency

    # Dạng sóng cơ bản (sin hoặc sawtooth)
    if instrument == "piano":
        signal = np.sin(2 * np.pi * frequency * t)
    elif instrument == "guitar":
        signal = sum(np.sin(2 * np.pi * frequency * (k + 1) * t) / (k + 1) for k in range(5))  # Harmonics

    # Thêm đường bao ADSR
    attack = int(0.1 * sample_rate)
    decay = int(0.2 * sample_rate)
    sustain_level = 0.7
    release = int(0.1 * sample_rate)
    sustain = len(t) - (attack + decay + release)

    envelope = np.concatenate([ 
        np.linspace(0, 1, attack),  # Attack
        np.linspace(1, sustain_level, decay),  # Decay
        np.ones(sustain) * sustain_level,  # Sustain
        np.linspace(sustain_level, 0, release)  # Release
    ])
    signal *= envelope[:len(t)]  # Áp dụng đường bao

    # Chuẩn hóa tín hiệu
    signal = np.int16(signal / np.max(np.abs(signal)) * 32767)
    return signal

# Hàm lưu tín hiệu vào file .wav
def save_wave(file_name, signal, sample_rate):
    with wave.open(file_name, 'w') as wav_file:
        num_channels = 1
        sampwidth = 2
        num_frames = len(signal)
        comptype = "NONE"
        compname = "not compressed"
        
        wav_file.setparams((num_channels, sampwidth, sample_rate, num_frames, comptype, compname))
        for s in signal:
            wav_file.writeframes(struct.pack('h', s))

# Hàm xử lý file input và tạo file .wav
def create_music_from_file(input_file, instrument="piano"):
    sample_rate = 44100  # Tần số mẫu
    signal = []
    output_file = f"{input_file.split('.')[0]}_{instrument}.wav"

    # Đọc file input và xử lý từng nốt nhạc
    with open(input_file, 'r') as file:
        for line in file:
            note, duration = line.split()
            duration = int(duration)  # Thời gian phát của nốt nhạc (ms)
            duration_sec = duration / 1000
            note_signal = generate_sound(note, duration_sec, sample_rate, instrument)
            signal.extend(note_signal)

    # Lưu kết quả vào file .wav
    save_wave(output_file, np.array(signal), sample_rate)
    return output_file

# Hàm mở hộp thoại chọn file
def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    entry_file.delete(0, tk.END)
    entry_file.insert(0, file_path)

# Hàm tạo nhạc và lưu vào file
def generate_music():
    input_file = entry_file.get()
    instrument = instrument_var.get()

    if input_file:
        try:
            output_file = create_music_from_file(input_file, instrument)
            messagebox.showinfo("Success", f"File {output_file} đã được tạo thành công!")
        except Exception as e:
            messagebox.showerror("Error", f"Đã xảy ra lỗi: {e}")
    else:
        messagebox.showerror("Error", "Vui lòng nhập đầy đủ thông tin!")

# Tạo giao diện GUI
root = tk.Tk()
root.title("Music Generator")
root.geometry("500x400")

# File input
label_file = tk.Label(root, text="Chọn file nhạc (TXT):", font=("Helvetica", 12))
label_file.pack(pady=10)

entry_file = tk.Entry(root, width=40, font=("Helvetica", 12))
entry_file.pack()

browse_button = tk.Button(root, text="Chọn File", command=browse_file, font=("Helvetica", 12), bg="#4CAF50", fg="white")
browse_button.pack(pady=5)

# Loại nhạc cụ
label_instrument = tk.Label(root, text="Chọn nhạc cụ:", font=("Helvetica", 12))
label_instrument.pack(pady=10)

instrument_var = tk.StringVar(value="piano")
radio_piano = tk.Radiobutton(root, text="Piano", variable=instrument_var, value="piano", font=("Helvetica", 12))
radio_piano.pack()

radio_guitar = tk.Radiobutton(root, text="Guitar", variable=instrument_var, value="guitar", font=("Helvetica", 12))
radio_guitar.pack()

# Nút tạo nhạc
generate_button = tk.Button(root, text="Tạo nhạc", command=generate_music, font=("Helvetica", 14), bg="#FF5722", fg="white")
generate_button.pack(pady=20)

# Khởi động giao diện
root.mainloop()