export const PageWrapper = ({ children }: { children: React.ReactNode }) => {
  return (
    <section className="min-h-screen flex items-center justify-center flex-1 bg-white overflow-x-hidden">
      {children}
    </section>
  );
};
