import { z } from "zod";

export const loginSchema = z.object({
    nik: z.string().length(16, "NIK harus 16 digit angka"),
    dob: z.string().min(1, "Tanggal lahir wajib diisi"),
});

export type LoginData = z.infer<typeof loginSchema>;
