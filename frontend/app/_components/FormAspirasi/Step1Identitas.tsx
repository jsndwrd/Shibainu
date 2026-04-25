import { step1Schema } from "@/schemas/aspirasiSchema";
import { useAspirasiStore } from "@/store/useAspirasiStore";
import { zodResolver } from "@hookform/resolvers/zod";
import { User } from "lucide-react";
import { useForm } from "react-hook-form";
import z from "zod";

const Step1Identitas = () => {
    type Step1FormValues = z.infer<typeof step1Schema>;

    const { formData, updateData, nextStep } = useAspirasiStore();
    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm({
        resolver: zodResolver(step1Schema),
        defaultValues: formData as Step1FormValues,
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
                <User className="h-5 w-5" /> <h3>Identitas Pelapor</h3>
            </div>
            <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
                <div>
                    <label className="mb-2 block text-sm font-medium text-gray-700">
                        Nama Lengkap (Sesuai KTP)
                    </label>
                    <input
                        {...register("namaLengkap")}
                        readOnly
                        className="w-full rounded-lg border border-gray-200 bg-gray-100 p-3 text-gray-600"
                    />
                </div>
                <div>
                    <label className="mb-2 block text-sm font-medium text-gray-700">
                        NIK (Tersensor)
                    </label>
                    <input
                        {...register("nik")}
                        readOnly
                        className="w-full rounded-lg border border-gray-200 bg-gray-100 p-3 text-gray-600"
                    />
                </div>
            </div>

            {/* Tambahan dari Panduan LAPOR! */}
            <div className="mt-4 flex gap-6">
                <label className="flex items-center gap-2 text-sm text-gray-700">
                    <input
                        type="checkbox"
                        {...register("isAnonim")}
                        className="text-primary h-4 w-4 rounded"
                    />
                    Anonimkan Nama Saya
                </label>
                <label className="flex items-center gap-2 text-sm text-gray-700">
                    <input
                        type="checkbox"
                        {...register("isRahasia")}
                        className="text-primary h-4 w-4 rounded"
                    />
                    Rahasiakan Laporan Ini (Private)
                </label>
            </div>

            <div className="flex justify-end border-t border-gray-100 pt-6">
                <button
                    type="submit"
                    className="bg-primary hover:bg-primary/80 rounded-lg px-6 py-3 font-medium text-white"
                >
                    Lanjutkan ke Detail
                </button>
            </div>
        </form>
    );
};

export default Step1Identitas;
