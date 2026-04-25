"use client";
import FormAspirasi from "@/app/_components/FormAspirasi";
import { useAuthStore } from "@/store/useAuthStore";
import { redirect } from "next/navigation";

export default function LaporanPage() {
  const { isAdmin } = useAuthStore();
  if (isAdmin) {
    redirect("/admin");
  }
  return (
    <section>
      <FormAspirasi />
    </section>
  );
}
