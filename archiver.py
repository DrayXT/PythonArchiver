import os
import sys
import time
import argparse
import tempfile
import bz2
import tarfile
from compression import zstd

def FileCompression(input_path, output_path, method, benchmark=False):
    start = time.time()
    if method == 'zstd':
        with open(input_path, 'rb') as fi, open(output_path, 'wb') as fo:
            data = fi.read()
            compressed = zstd.compress(data)
            fo.write(compressed)
    elif method == 'bz2':
        with open(input_path, 'rb') as fi, bz2.open(output_path, 'wb') as fo:
            fo.write(fi.read())
    if benchmark:
        print(f"Compression time: {time.time() - start:.2f}s")

def FileDecompression(input_path, output_path, method, benchmark=False):
    start = time.time()
    if method == 'zstd':
        with open(input_path, 'rb') as fi, open(output_path, 'wb') as fo:
            data = fi.read()
            fo.write(zstd.decompress(data))
    elif method == 'bz2':
        with bz2.open(input_path, 'rb') as fi, open(output_path, 'wb') as fo:
            fo.write(fi.read())
    if benchmark:
        print(f"Decompression time: {time.time() - start:.2f}s")

def DirCompression(input_dir, output_path, method, benchmark=False):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".tar") as temp_tar:
            tar_path = temp_tar.name
        with tarfile.open(tar_path, 'w') as tar:
            tar.add(input_dir, arcname=os.path.basename(input_dir))
        FileCompression(tar_path, output_path, method, benchmark)
        os.remove(tar_path)
    except Exception as e:
        print(f"\nAn error occurred when archiving '{input_dir}': {e}")
        sys.exit(1)

def DirDecompression(input_path, output_dir, method, benchmark=False):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".tar") as temp_tar:
            tar_path = temp_tar.name
        FileDecompression(input_path, tar_path, method, benchmark)
        with tarfile.open(tar_path, 'r') as tar:
            tar.extractall(path=output_dir)
        os.remove(tar_path)
    except Exception as e:
        print(f"\nAn error occurred when unpacking '{input_path}': {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Archiver, supports .zst and .bz2 formats")
    parser.add_argument("src", help="source file/folder or archive to unpack")
    parser.add_argument("trg", help="target file or directory")
    parser.add_argument("-b", "--benchmark", action="store_true", help="show execution time")
    args = parser.parse_args()
    src, trg, bench = args.src, args.trg, args.benchmark

    if not os.path.exists(src):
        print(f"The source path '{src}' doesn't exist")
        sys.exit(1)

    mode = src.endswith('.zst') or src.endswith('.bz2')
    if mode:
        if src.endswith('.zst'):
            method = 'zstd'
        elif src.endswith('.bz2'):
            method = 'bz2'
        else:
            print("Unsupported archive format")
            sys.exit(1)
        try:
            tar_check = tarfile.open(src)
            tar_check.close()
            os.makedirs(trg, exist_ok=True)
            DirDecompression(src, trg, method, bench)
        except tarfile.ReadError:
            FileDecompression(src, trg, method, bench)
    else:
        if trg.endswith('.zst'):
            method = 'zstd'
        elif trg.endswith('.bz2'):
            method = 'bz2'
        else:
            print(".zst or .bz2 formats only")
            sys.exit(1)
        if os.path.isdir(src):
            DirCompression(src, trg, method, bench)
        else:
            FileCompression(src, trg, method, bench)

if __name__ == "__main__":
    main()
