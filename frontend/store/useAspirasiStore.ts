import { create } from "zustand";
import { AspirasiData } from "@/schemas/aspirasiSchema";

interface FormState {
    step: number;
    formData: Partial<AspirasiData>;
    setStep: (step: number) => void;
    nextStep: () => void;
    prevStep: () => void;
    updateData: (data: Partial<AspirasiData>) => void;
    resetForm: () => void;
}

export const useAspirasiStore = create<FormState>((set) => ({
    step: 1,
    formData: {
        namaLengkap: "Ananda Rizky Pratama",
        nik: "3275238291323001",
        tingkatUrgensi: "Sedang",
    },
    setStep: (step) => set({ step }),
    nextStep: () => set((state) => ({ step: state.step + 1 })),
    prevStep: () => set((state) => ({ step: Math.max(1, state.step - 1) })),
    updateData: (data) =>
        set((state) => ({ formData: { ...state.formData, ...data } })),
    resetForm: () => set({ step: 1, formData: {} }),
}));
