import { step2Schema } from "@/schemas/aspirasiSchema";
import { useAspirasiStore } from "@/store/useAspirasiStore";
import { zodResolver } from "@hookform/resolvers/zod";
import { FileText } from "lucide-react";
import { useForm } from "react-hook-form";
import z from "zod";

const Step2Detail = () => {
    type Step2FormValues = z.infer<typeof step2Schema>;

    const { formData, updateData, nextStep, prevStep } = useAspirasiStore();
    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm({
        resolver: zodResolver(step2Schema),
        defaultValues: formData as Step2FormValues,
    });

    return (
        <form
            onSubmit={handleSubmit((d) => {
                updateData(d);
                nextStep();
            })}
            className="space-y-6"
        >
            <div className="mb-4 flex items-center gap-2 font-semibold text-emerald-800">
                <FileText className="h-5 w-5" /> <h3>Detail Aspirasi</h3>
            </div>

            <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
                <div>
                    <label className="mb-2 block text-sm font-medium text-gray-700">
                        Kategori Aspirasi
                    </label>
                    <select
                        {...register("kategoriAspirasi")}
                        className="w-full rounded-lg border border-gray-300 bg-white p-3 outline-none focus:ring-2 focus:ring-emerald-500"
                    >
                        <option value="">Pilih Kategori</option>
                        <option value="infrastruktur">Infrastruktur</option>
                        <option value="kesehatan">Kesehatan</option>
                    </select>
                    {errors.kategoriAspirasi && (
                        <p className="mt-1 text-xs text-red-500">
                            {errors.kategoriAspirasi.message as string}
                        </p>
                    )}
                </div>
                <div>
                    <label className="mb-2 block text-sm font-medium text-gray-700">
                        Tingkat Pemerintahan
                    </label>
                    <div className="flex rounded-lg bg-gray-100 p-1">
                        {["Nasional", "Provinsi", "Kota/Kab"].map((lvl) => (
                            <label
                                key={lvl}
                                className="flex-1 cursor-pointer text-center"
                            >
                                <input
                                    type="radio"
                                    value={lvl}
                                    {...register("tingkatPemerintahan")}
                                    className="peer sr-only"
                                />
                                <div className="rounded-md py-2 text-sm font-medium text-gray-500 transition-all peer-checked:bg-white peer-checked:text-emerald-700 peer-checked:shadow-sm">
                                    {lvl}
                                </div>
                            </label>
                        ))}
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
                <div>
                    <label className="mb-2 block text-sm font-medium text-gray-700">
                        Judul Laporan
                    </label>
                    <input
                        {...register("judulLaporan")}
                        placeholder="Kesimpulan singkat aduan"
                        className="w-full rounded-lg border border-gray-300 p-3 outline-none focus:ring-2 focus:ring-emerald-500"
                    />
                    {errors.judulLaporan && (
                        <p className="mt-1 text-xs text-red-500">
                            {errors.judulLaporan.message as string}
                        </p>
                    )}
                </div>
                <div>
                    <label className="mb-2 block text-sm font-medium text-gray-700">
                        Tanggal Kejadian
                    </label>
                    <input
                        type="date"
                        {...register("tanggalKejadian")}
                        className="w-full rounded-lg border border-gray-300 p-3 outline-none focus:ring-2 focus:ring-emerald-500"
                    />
                    {errors.tanggalKejadian && (
                        <p className="mt-1 text-xs text-red-500">
                            {errors.tanggalKejadian.message as string}
                        </p>
                    )}
                </div>
            </div>

            <div>
                <label className="mb-2 block text-sm font-medium text-gray-700">
                    Deskripsi Aspirasi
                </label>
                <textarea
                    {...register("deskripsi")}
                    rows={5}
                    placeholder="Ceritakan secara detail mengenai aspirasi, masukan, atau kendala..."
                    className="w-full rounded-lg border border-gray-300 p-3 outline-none focus:ring-2 focus:ring-emerald-500"
                ></textarea>
                {errors.deskripsi && (
                    <p className="mt-1 text-xs text-red-500">
                        {errors.deskripsi.message as string}
                    </p>
                )}
            </div>

            <div>
                <label className="mb-2 block text-sm font-medium text-gray-700">
                    Lampiran (Opsional)
                </label>
                <input
                    type="file"
                    {...register("lampiran")}
                    className="text-sm file:mr-4 file:rounded-lg file:border-0 file:bg-emerald-50 file:px-4 file:py-2 file:text-sm file:font-semibold file:text-emerald-700 hover:file:bg-emerald-100"
                />
            </div>

            <div className="flex justify-between border-t border-gray-100 pt-6">
                <button
                    type="button"
                    onClick={prevStep}
                    className="rounded-lg border border-gray-300 px-6 py-3 font-medium text-gray-700 hover:bg-gray-50"
                >
                    Kembali
                </button>
                <button
                    type="submit"
                    className="rounded-lg bg-emerald-700 px-6 py-3 font-medium text-white hover:bg-emerald-800"
                >
                    Lanjutkan ke Lokasi
                </button>
            </div>
        </form>
    );
};

export default Step2Detail;
