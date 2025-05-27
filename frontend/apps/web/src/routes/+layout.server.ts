export const load = async (event) => {
  return {
    environment: event.locals.environment
  };
};
