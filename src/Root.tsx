import { NiftyShortComposition } from "./NiftyShort";
import { DashShortComposition } from "./DashShort";
import { DashInsertComposition } from "./DashInsert";
import { DiwaliWatchlistComposition } from "./DiwaliWatchlist";

export const RemotionRoot: React.FC = () => (
  <>
    <NiftyShortComposition />
    <DashShortComposition />
    <DashInsertComposition />
    <DiwaliWatchlistComposition />
  </>
);
