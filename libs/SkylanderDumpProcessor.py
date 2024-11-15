import argparse
import binascii
import struct
import warnings
import libs.sklykeys as sklykeys

class SkylanderDumpProcessor:
    def __init__(self, blank_path, sky_path, output_name):
        self.blank_path = blank_path
        self.sky_path = sky_path
        self.output_name = output_name
        self.clean_tag = None
        self.skylander_dump = None

    def calculate_bcc(self, bcc):
        return (bcc[0] ^ bcc[1] ^ bcc[2] ^ bcc[3])

    def check_keys(self, a_or_b, data):
        block_offset = 0x0
        if a_or_b == 'b':
            block_offset = 0x0A
        data.seek(0)
        verified = True
        for sector in range(0, 16):
            data.seek(0x30, 1)
            data.seek(block_offset, 1)
            key = binascii.hexlify(data.read(0x06)).decode("utf-8")
            data.seek(0xA - block_offset, 1)
            verified = verified | (key == "000000000000" or key.upper() == "FFFFFFFFFFFF")
        return verified

    def process(self):
        # Load files
        self.clean_tag = open(self.blank_path, 'rb')
        self.skylander_dump = open(self.sky_path, 'rb')

        # Check if A and B keys are standard
        verify_keys_a = self.check_keys('a', self.clean_tag)
        verify_keys_b = self.check_keys('b', self.clean_tag)

        if not verify_keys_a or not verify_keys_b:
            warnings.warn("Some of the keys in the blank dump are not standard!")

        # Reset seek position to the beginning of the file
        self.clean_tag.seek(0)

        # Read UID, BCC, SAK, ATQA
        bytes_uid = self.clean_tag.read(0x04)
        written_bcc = self.clean_tag.read(0x01)
        hex_written_bcc = binascii.hexlify(written_bcc)
        sak = self.clean_tag.read(0x01)
        atqa = self.clean_tag.read(0x02)

        hex_uid = binascii.hexlify(bytes_uid)
        string_uid = hex_uid.decode("utf-8")

        print("UID:", "0x" + string_uid.upper())
        print("BCC:", "0x" + hex_written_bcc.decode("utf-8").upper())
        print("SAK:", "0x" + binascii.hexlify(sak).decode("utf-8").upper())
        print("ATQA:", "0x" + binascii.hexlify(struct.pack('<H', int.from_bytes(atqa, "big"))).decode("utf-8").upper())

        # Calculate and check BCC
        calculated_bcc = self.calculate_bcc(bytes_uid)
        bcc_is_good = calculated_bcc == int(hex_written_bcc, 16)
        if not bcc_is_good:
            warnings.warn("This Tag's BCC is incorrect! Possibly a 7 byte UID?")

        # Read the locked zero block
        self.clean_tag.seek(0)
        locked_zero_block = self.clean_tag.read(0x10)
        self.clean_tag.close()

        # Now, handle the skylander dump
        self.skylander_dump.seek(0)
        new_file = open(self.output_name + ".dump", "wb")

        # Prime the new file with the entire Skylander dump
        new_file.write(self.skylander_dump.read(1024))

        # Write the blank tag's manufacturer block to the new file
        new_file.seek(0)
        new_file.write(locked_zero_block)

        self.skylander_dump.seek(0x10)
        skylander_info = self.skylander_dump.read(0x0E)
        self.skylander_dump.close()

        zero_checksum_data = locked_zero_block + skylander_info

        # Write the type 0 checksum for the new data
        binary_crc16 = int.to_bytes(struct.unpack("<H", struct.pack(">H", binascii.crc_hqx(zero_checksum_data, 0xFFFF)))[0], 2, "big")
        new_file.seek(0x0E, 1)
        new_file.write(binary_crc16)

        # Generate new keys for the blank tag's UID
        keys = sklykeys.generate_keys(string_uid)

        print("New keys:", keys)

        # Set new keys in the new file
        new_file.seek(0)
        for i in range(0, 16):
            new_file.seek(0x30, 1)
            new_file.write(binascii.unhexlify(keys[i]))
            new_file.seek(0xA, 1)

        new_file.seek(0x36)
        new_file.write(binascii.unhexlify("FF0780"))

        new_file.close()
