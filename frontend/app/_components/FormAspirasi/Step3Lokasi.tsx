import { step3Schema } from "@/schemas/aspirasiSchema";
import { useAspirasiStore } from "@/store/useAspirasiStore";
import { zodResolver } from "@hookform/resolvers/zod";
import { MapPin } from "lucide-react";
import { useForm } from "react-hook-form";
import z from "zod";

const Step3Lokasi = () => {
    type Step3FormValues = z.infer<typeof step3Schema>;
    const { formData, updateData, nextStep, prevStep } = useAspirasiStore();
    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm({
        resolver: zodResolver(step3Schema),
        defaultValues: formData as Step3FormValues,
    });

    return (
        <form
            onSubmit={handleSubmit((d) => {
                updateData(d);
                nextStep();
            })}
            className="space-y-6"
        >
            <div className="text-primary mb-4 flex items-center gap-2 font-semibold">
                <MapPin className="h-5 w-5" /> <h3>Lokasi & Tingkat Urgensi</h3>
            </div>

            <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
                <div>
                    <label className="mb-2 block text-sm font-medium text-gray-700">
                        Provinsi
                    </label>
                    <select
                        {...register("provinsi")}
                        className="focus:ring-accent w-full rounded-lg border border-gray-300 bg-white p-3 outline-none focus:ring-2"
                    >
                        <option value="Jawa Barat">Jawa Barat</option>
                        {/* ... other options */}
                    </select>
                </div>
                <div>
                    <label className="mb-2 block text-sm font-medium text-gray-700">
                        Kota / Kabupaten
                    </label>
                    <select
                        {...register("kota")}
                        className="focus:ring-accent w-full rounded-lg border border-gray-300 bg-white p-3 outline-none focus:ring-2"
                    >
                        <option value="Kota Bekasi">Kota Bekasi</option>
                        {/* ... other options */}
                    </select>
                </div>
            </div>

            <div>
                <label className="mb-2 block text-sm font-medium text-gray-700">
                    Lokasi Kejadian Lengkap
                </label>
                <input
                    {...register("lokasiDetail")}
                    placeholder="Nama jalan, gedung, atau patokan spesifik"
                    className="focus:ring-accent w-full rounded-lg border border-gray-300 p-3 outline-none focus:ring-2"
                />
                {errors.lokasiDetail && (
                    <p className="mt-1 text-xs text-red-500">
                        {errors.lokasiDetail.message as string}
                    </p>
                )}
            </div>

            <div className="grid grid-cols-1 gap-8 md:grid-cols-2">
                {/* Urgensi Slider UI Mock */}
                <div>
                    <div className="mb-2 flex items-center justify-between">
                        <label className="block text-sm font-medium text-gray-700">
                            Tingkat Urgensi
                        </label>
                        <span className="rounded bg-red-100 px-2 py-1 text-[10px] font-bold text-red-700">
                            SANGAT PENTING
                        </span>
                    </div>
                    <input
                        type="range"
                        min="0"
                        max="2"
                        step="1"
                        {...register("tingkatUrgensi")}
                        className="accent-primary w-full"
                    />
                    <div className="mt-1 flex justify-between text-xs text-gray-500">
                        <span>Rendah</span>
                        <span>Sedang</span>
                        <span>Kritis</span>
                    </div>
                </div>

                <div>
                    <label className="mb-2 block text-sm font-medium text-gray-700">
                        Instansi Tujuan (Opsional)
                    </label>
                    <input
                        {...register("instansiTujuan")}
                        placeholder="Contoh: Kementerian PUPR"
                        className="focus:ring-accent w-full rounded-lg border border-gray-300 p-3 outline-none focus:ring-2"
                    />
                </div>
            </div>

            <div>
                <label className="mb-3 block text-sm font-medium text-gray-700">
                    Cakupan Dampak
                </label>
                <div className="grid grid-cols-2 gap-4">
                    {[
                        { id: "Individu", desc: "Berdampak pada diri sendiri" },
                        { id: "Komunitas", desc: "Lingkungan RT/RW/Desa" },
                        { id: "Wilayah", desc: "Satu Kota atau Provinsi" },
                        { id: "Nasional", desc: "Berdampak ke seluruh RI" },
                    ].map((item) => (
                        <label
                            key={item.id}
                            className="relative block cursor-pointer"
                        >
                            <input
                                type="radio"
                                value={item.id}
                                {...register("cakupanDampak")}
                                className="peer sr-only"
                            />
                            <div className="peer-checked:border-accent rounded-lg border border-gray-200 p-4 transition-colors peer-checked:bg-emerald-50">
                                <p className="text-sm font-semibold text-gray-900">
                                    {item.id}
                                </p>
                                <p className="mt-1 text-xs text-gray-500">
                                    {item.desc}
                                </p>
                            </div>
                        </label>
                    ))}
                </div>
            </div>

            <div className="flex justify-between border-t border-gray-100 pt-6">
                <button
                    type="button"
                    className="border-primary text-primary rounded-lg border px-6 py-3 font-medium hover:bg-emerald-50"
                >
                    Simpan Draft
                </button>
                <div className="flex gap-3">
                    <button
                        type="button"
                        onClick={prevStep}
                        className="rounded-lg border border-gray-300 px-6 py-3 font-medium text-gray-700 hover:bg-gray-50"
                    >
                        Kembali
                    </button>
                    <button
                        type="submit"
                        className="bg-primary hover:bg-primary/90 rounded-lg px-6 py-3 font-medium text-white"
                    >
                        Lanjutkan ke Review
                    </button>
                </div>
            </div>
        </form>
    );
};

export default Step3Lokasi;
