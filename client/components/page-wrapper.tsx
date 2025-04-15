export const PageWrapper = ({ children }: { children: React.ReactNode }) => {
  return (
    <section className="w-screen h-screen flex items-center justify-center flex-1 bg-white ">
      {children}
    </section>
  );
};
