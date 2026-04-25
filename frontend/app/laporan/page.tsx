import FormAspirasi from "@/app/_components/FormAspirasi";

export const metadata = {
  title: "Buat Laporan | Vokara",
  description: "Sampaikan aspirasi Anda kepada pemerintah secara transparan.",
};

export default function LaporanPage() {
  return (
    <section>
      <FormAspirasi />
    </section>
  );
}
