"use client";

import FormLayout from "./FormLayout";
import Step1Identitas from "./Step1Identitas";
import Step2Detail from "./Step2Detail";
import Step3Lokasi from "./Step3Lokasi";
import { useAspirasiStore } from "@/store/useAspirasiStore";
import Step4Review from "./Step4Review";

export default function FormAspirasi() {
    const { step } = useAspirasiStore();

    return (
        <FormLayout>
            {step === 1 && <Step1Identitas />}
            {step === 2 && <Step2Detail />}
            {step === 3 && <Step3Lokasi />}
            {step === 4 && <Step4Review />}
        </FormLayout>
    );
}
