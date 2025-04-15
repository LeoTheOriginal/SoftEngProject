export const PageWrapper = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="w-full h-screen flex items-center justify-center bg-white gap">
      {children}
    </div>
  );
};
