import { useAspirasiStore } from "@/store/useAspirasiStore";
import { useMutation } from "@tanstack/react-query";
import { CheckCircle } from "lucide-react";

const Step4Review = () => {
    const { formData, prevStep, resetForm } = useAspirasiStore();

    const mutation = useMutation({
        mutationFn: async (data: any) => {
            // Mock API call
            return new Promise((res) => setTimeout(res, 2000));
        },
        onSuccess: () => {
            alert("Laporan berhasil dikirim ke sistem terpadu!");
            resetForm();
        },
    });

    return (
        <div className="space-y-6">
            <div className="text-primary mb-4 flex items-center gap-2 font-semibold">
                <CheckCircle className="h-5 w-5" /> <h3>Review Laporan Anda</h3>
            </div>

            <div className="space-y-4 rounded-xl border border-gray-200 bg-gray-50 p-6 text-sm">
                <div className="grid grid-cols-3 border-b border-gray-200 pb-3">
                    <span className="text-gray-500">Judul</span>
                    <span className="col-span-2 font-medium">
                        {formData.judulLaporan}
                    </span>
                </div>
                <div className="grid grid-cols-3 border-b border-gray-200 pb-3">
                    <span className="text-gray-500">Kategori & Instansi</span>
                    <span className="col-span-2 font-medium">
                        {formData.kategoriAspirasi} -{" "}
                        {formData.instansiTujuan || "Belum ditentukan"}
                    </span>
                </div>
                <div className="grid grid-cols-3 border-b border-gray-200 pb-3">
                    <span className="text-gray-500">Lokasi</span>
                    <span className="col-span-2 font-medium">
                        {formData.lokasiDetail}, {formData.kota},{" "}
                        {formData.provinsi}
                    </span>
                </div>
                <div className="grid grid-cols-3 border-b border-gray-200 pb-3">
                    <span className="text-gray-500">Privasi</span>
                    <span className="text-primary col-span-2 font-medium">
                        {formData.isAnonim ? "Anonim" : "Publik"} &{" "}
                        {formData.isRahasia ? "Rahasia" : "Terbuka"}
                    </span>
                </div>
            </div>

            <div className="flex justify-between border-t border-gray-100 pt-6">
                <button
                    onClick={prevStep}
                    disabled={mutation.isPending}
                    className="rounded-lg border border-gray-300 px-6 py-3 font-medium text-gray-700 hover:cursor-pointer hover:bg-gray-50"
                >
                    Ubah Data
                </button>
                <button
                    onClick={() => mutation.mutate(formData)}
                    disabled={mutation.isPending}
                    className="bg-primary hover:bg-primary/90 flex items-center gap-2 rounded-lg px-8 py-3 font-medium text-white hover:cursor-pointer disabled:cursor-not-allowed disabled:opacity-70"
                >
                    {mutation.isPending
                        ? "Memproses Enkripsi & Mengirim..."
                        : "Kirim Aspirasi Sekarang"}
                </button>
            </div>
        </div>
    );
};

export default Step4Review;
