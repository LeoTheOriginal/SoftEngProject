import { PageWrapper } from "@/components/page-wrapper";

export default function Home() {
  return (
    <PageWrapper>
      <div className="bg-[#949494]/40 p-48 shadow-lg w-[80%] flex flex-col gap-12">
        <h1 className="text-[#0C0C0D] text-6xl font-bold text-center">
          Platforma e-learningowa
        </h1>

        <div className="flex flex-row gap-4 justify-center">
          <a
            href="/login"
            className="py-2 px-4 bg-[#2C2C2C] text-white font-medium rounded-lg text-center"
          >
            Zaloguj się
          </a>

          <a
            href="/register"
            className="py-2 px-4 border border-[#2C2C2C] text-[#2C2C2C] font-medium rounded-lg text-center"
          >
            Rejestracja
          </a>
        </div>
      </div>
    </PageWrapper>
  );
}
